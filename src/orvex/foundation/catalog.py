"""Offline catalog: policy before projection, source deduplication and reviewed updates."""

import json
from dataclasses import replace
from uuid import uuid4
from .models import (
    Content,
    ContentUnavailable,
    Registration,
    ProposalConflict,
    KINDS,
    IMPORT_STATES,
    normalize,
    json_object,
    source_identity,
    valid_age,
    utc_now,
)
from .profiles import ProfileService

PATCH_FIELDS = frozenset(
    {
        "title",
        "alternate_title",
        "format",
        "metadata",
        "cover",
        "backdrop",
        "age",
        "import_state",
        "hidden",
    }
)


class CatalogService:
    def __init__(self, repository, profiles):
        self.repo = repository
        self.profiles = profiles

    def _allowed(self, item, profile, include_hidden=False):
        if not item or (item.hidden and not (include_hidden and profile.kind == "adult")):
            return False
        if not ProfileService.allows(profile, item):
            return False
        if item.parent_id:
            parent = self.repo.raw(item.parent_id)
            return bool(
                parent
                and parent.kind == "series"
                and not parent.hidden
                and ProfileService.allows(profile, parent)
            )
        return True

    def get(self, content_id, profile_id, include_hidden=False):
        try:
            profile = self.profiles.get(profile_id)
        except PermissionError:
            raise ContentUnavailable("Contenido no disponible.") from None
        item = self.repo.raw(content_id)
        if not self._allowed(item, profile, include_hidden):
            raise ContentUnavailable("Contenido no disponible.")
        return item

    def query(
        self,
        profile_id,
        kind=None,
        query="",
        format=None,
        favorites_only=False,
        include_hidden=False,
        import_state=None,
    ):
        try:
            profile = self.profiles.get(profile_id)
        except PermissionError:
            return []
        favorites = self.repo.favorites(profile_id)
        needle = normalize(query.strip())
        result = []
        for item in self.repo.all():
            if not self._allowed(item, profile, include_hidden):
                continue
            if kind and item.kind != kind:
                continue
            if format is not None and item.format != format:
                continue
            if import_state and item.import_state != import_state:
                continue
            if needle not in normalize(item.title + " " + item.alternate_title):
                continue
            if favorites_only and item.id not in favorites:
                continue
            result.append(item)
        return sorted(result, key=lambda c: (normalize(c.title), c.id))

    def options(self, profile_id, kind=None):
        return sorted({c.format for c in self.query(profile_id, kind=kind) if c.format})

    def register(
        self,
        actor_id,
        *,
        kind,
        title,
        source_type,
        source_ref,
        format="",
        alternate_title="",
        metadata=None,
        cover=None,
        backdrop=None,
        age=None,
        import_state="registered",
        parent_id=None,
    ):
        self.profiles.require_adult(actor_id)
        key = source_identity(source_type, source_ref)
        if kind not in KINDS:
            raise ValueError("Tipo de contenido no válido.")
        if (kind == "episode") != bool(parent_id):
            raise ValueError("Un episodio necesita su serie; los otros tipos no admiten padre.")
        if parent_id:
            parent = self.get(parent_id, actor_id, True)
            if parent.kind != "series":
                raise ValueError("El padre debe ser una serie.")
        item = Content(
            "content-" + uuid4().hex,
            kind,
            title,
            alternate_title,
            format,
            source_type,
            source_ref,
            json_object(metadata if metadata is not None else {}),
            cover,
            backdrop,
            age,
            import_state,
            False,
            parent_id,
            utc_now(),
        )
        self._validate(item)
        with self.repo.store.transaction():
            for existing in self.repo.all():
                try:
                    same = (
                        existing.source_type == source_type
                        and source_identity(existing.source_type, existing.source_ref) == key
                    )
                except ValueError:
                    same = False
                if same:
                    if existing.kind != kind:
                        raise ValueError("Ese origen ya pertenece a otro tipo de contenido.")
                    return Registration(existing, False)
            self.repo.insert(item, key)
        return Registration(item, True)

    def find_duplicates(self, profile_id):
        """Report legacy/canonical source collisions without merging or deleting user data."""
        groups = {}
        for item in self.query(profile_id, include_hidden=True):
            try:
                key = (item.source_type, source_identity(item.source_type, item.source_ref))
            except ValueError:
                continue
            groups.setdefault(key, []).append(item)
        return [tuple(items) for items in groups.values() if len(items) > 1]

    def favorite(self, content_id, profile_id, value):
        self.get(content_id, profile_id)
        if not isinstance(value, bool):
            raise ValueError("Favorito debe ser booleano.")
        self.repo.favorite(profile_id, content_id, value)

    def record_activity(
        self, content_id, profile_id, event="opened", duration_ms=None, evidence="manual"
    ):
        self.get(content_id, profile_id)
        if event not in ("opened", "started", "finished") or evidence not in ("manual", "observed"):
            raise ValueError("Actividad o evidencia no válida.")
        if duration_ms is not None and (
            not isinstance(duration_ms, int)
            or isinstance(duration_ms, bool)
            or duration_ms < 0
            or duration_ms > 2**63 - 1
        ):
            raise ValueError("Duración no válida.")
        if duration_ms is not None and event != "finished":
            raise ValueError("La duración requiere una actividad finalizada.")
        with self.repo.store.transaction():
            key = "activity-" + uuid4().hex
            self.repo.db.execute(
                "INSERT INTO content_activity VALUES(?,?,?,?,?,?,?)",
                (key, profile_id, content_id, event, utc_now(), duration_ms, evidence),
            )
        return key

    def activity(self, profile_id):
        try:
            profile = self.profiles.get(profile_id)
        except PermissionError:
            return []
        return [
            r
            for r in self.repo.activity(profile_id)
            if self._allowed(self.repo.raw(r["content_id"]), profile)
        ]

    def recent(self, profile_id, limit=20):
        if not isinstance(limit, int) or isinstance(limit, bool) or not 0 <= limit <= 1000:
            raise ValueError("Límite no válido.")
        result = []
        seen = set()
        for row in self.activity(profile_id):
            if row["content_id"] not in seen:
                seen.add(row["content_id"])
                result.append(self.get(row["content_id"], profile_id))
        return result[:limit]

    def propose_metadata(self, content_id, actor_id, changes, source):
        self.profiles.require_adult(actor_id)
        item = self.get(content_id, actor_id, True)
        changes = json_object(changes)
        if not changes or set(changes) - PATCH_FIELDS:
            raise ValueError("Campos de propuesta no admitidos.")
        if not isinstance(source, str) or not source.strip() or len(source) > 1000:
            raise ValueError("Indica la fuente de la propuesta.")
        if "metadata" in changes:
            changes["metadata"] = {**dict(item.metadata), **json_object(changes["metadata"])}
        self._validate(replace(item, **changes))
        proposal_id = "proposal-" + uuid4().hex
        with self.repo.store.transaction():
            self.repo.db.execute(
                """INSERT INTO metadata_proposals(id,content_id,changes,source,expected_fingerprint,created_at)
                VALUES(?,?,?,?,?,?)""",
                (
                    proposal_id,
                    content_id,
                    json.dumps(changes, ensure_ascii=False, allow_nan=False),
                    source,
                    item.fingerprint,
                    utc_now(),
                ),
            )
        return proposal_id

    def proposal(self, proposal_id, actor_id):
        self.profiles.require_adult(actor_id)
        row = self.repo.proposal(proposal_id)
        if not row:
            raise ContentUnavailable("Propuesta no disponible.")
        self.get(row["content_id"], actor_id, True)
        return dict(row, changes=json.loads(row["changes"]))

    def decide_proposal(self, proposal_id, actor_id, approve):
        self.profiles.require_adult(actor_id)
        if not isinstance(approve, bool):
            raise ValueError("La decisión debe ser explícita.")
        with self.repo.store.transaction():
            row = self.proposal(proposal_id, actor_id)
            if row["state"] != "pending":
                raise ProposalConflict("Propuesta ya resuelta.")
            item = self.get(row["content_id"], actor_id, True)
            if approve:
                if item.fingerprint != row["expected_fingerprint"]:
                    raise ProposalConflict("El contenido cambió; revisa una propuesta nueva.")
                updated = replace(item, **row["changes"])
                self._validate(updated)
                self.repo.update(updated)
            self.repo.db.execute(
                "UPDATE metadata_proposals SET state=?,decided_at=?,decided_by=? WHERE id=?",
                ("approved" if approve else "rejected", utc_now(), actor_id, proposal_id),
            )
        return self.get(item.id, actor_id, True)

    @staticmethod
    def _validate(item):
        for name, limit in [("title", 120), ("alternate_title", 240), ("format", 80)]:
            value = getattr(item, name)
            if (
                not isinstance(value, str)
                or len(value) > limit
                or "\x00" in value
                or (name == "title" and not value.strip())
            ):
                raise ValueError("Texto no válido: " + name)
        if item.age is not None and not valid_age(item.age):
            raise ValueError("Clasificación etaria no válida.")
        if not isinstance(item.hidden, bool) or item.import_state not in IMPORT_STATES:
            raise ValueError("Estado no válido.")
        for asset in (item.cover, item.backdrop):
            if asset is not None and (
                not isinstance(asset, str) or len(asset) > 4096 or "\x00" in asset
            ):
                raise ValueError("Recurso gráfico no válido.")
        json_object(item.metadata)
