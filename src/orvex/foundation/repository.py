"""SQLite persistence adapters. Legacy games are projected, never copied to content_items."""

import json
from .models import Content, json_object


class SQLiteRepository:
    def __init__(self, store):
        self.store = store
        self.db = store.db

    def profile(self, profile_id):
        return self._one("SELECT * FROM profiles WHERE id=?", (profile_id,))

    def profiles(self):
        return self._all("SELECT * FROM profiles WHERE enabled=1 ORDER BY id")

    def create_profile(self, *values):
        with self.store.transaction():
            self.db.execute(
                "INSERT INTO profiles(id,kind,name,max_age,created_at) VALUES(?,?,?,?,?)", values
            )

    def _one(self, sql, params=()):
        cursor = self.db.execute(sql, params)
        row = cursor.fetchone()
        return dict(zip([col[0] for col in cursor.description], row)) if row else None

    def _all(self, sql, params=()):
        cursor = self.db.execute(sql, params)
        keys = [col[0] for col in cursor.description]
        return [dict(zip(keys, row)) for row in cursor.fetchall()]

    def _content(self, row, legacy=False):
        try:
            metadata = json_object(row["metadata"])
        except ValueError:
            metadata = {}
            self.store.warnings.append("Metadatos no válidos: " + row["id"])
        source_ref = row.get("source_ref", row.get("executable", ""))
        source_type = row.get("source_type", "local")
        if legacy:
            # These optional adapter tables remain owned by the existing adapters.
            tables = {
                r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            for table in ("dolphin_roms", "pcsx2_roms"):
                if table in tables:
                    ref = self.db.execute(
                        f"SELECT path FROM {table} WHERE game_id=?", (row["id"],)
                    ).fetchone()
                    if ref:
                        source_ref = ref[0]
                        break
        return Content(
            id=row["id"],
            kind="game" if legacy else row["kind"],
            title=row["name"] if legacy else row["title"],
            alternate_title=row.get("alternate_title") or "",
            format=row["platform"] if legacy else row["format"],
            source_type=source_type,
            source_ref=source_ref,
            metadata=metadata,
            cover=row["cover"],
            backdrop=row["backdrop"],
            age=row.get("age"),
            import_state=row.get("import_state") or "registered",
            hidden=bool(row["hidden"]),
            parent_id=row.get("parent_id"),
            created_at=row["created_at"],
            legacy_game=legacy,
        )

    def raw(self, content_id):
        row = self._one("SELECT * FROM content_items WHERE id=?", (content_id,))
        if row:
            return self._content(row)
        row = self._one(
            """SELECT g.*,d.alternate_title,d.age,d.import_state FROM real_games g
            LEFT JOIN game_catalog_details d ON g.id=d.game_id WHERE g.id=?""",
            (content_id,),
        )
        return self._content(row, True) if row else None

    def all(self):
        legacy = self._all("""SELECT g.*,d.alternate_title,d.age,d.import_state FROM real_games g
            LEFT JOIN game_catalog_details d ON g.id=d.game_id""")
        return [self._content(r, True) for r in legacy] + [
            self._content(r) for r in self._all("SELECT * FROM content_items")
        ]

    def insert(self, content, source_key):
        self.db.execute(
            """INSERT INTO content_items(id,kind,title,alternate_title,format,source_type,source_ref,source_key,
            metadata,cover,backdrop,age,import_state,hidden,parent_id,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                content.id,
                content.kind,
                content.title,
                content.alternate_title,
                content.format,
                content.source_type,
                content.source_ref,
                source_key,
                json.dumps(dict(content.metadata), ensure_ascii=False, allow_nan=False),
                content.cover,
                content.backdrop,
                content.age,
                content.import_state,
                int(content.hidden),
                content.parent_id,
                content.created_at,
            ),
        )

    def update(self, content):
        if content.legacy_game:
            self.db.execute(
                "UPDATE real_games SET name=?,platform=?,metadata=?,cover=?,backdrop=?,hidden=? WHERE id=?",
                (
                    content.title,
                    content.format,
                    json.dumps(dict(content.metadata), ensure_ascii=False),
                    content.cover,
                    content.backdrop,
                    int(content.hidden),
                    content.id,
                ),
            )
            self.db.execute(
                """INSERT INTO game_catalog_details(game_id,alternate_title,age,import_state,revision) VALUES(?,?,?,?,1)
                ON CONFLICT(game_id) DO UPDATE SET alternate_title=excluded.alternate_title,age=excluded.age,
                import_state=excluded.import_state,revision=game_catalog_details.revision+1""",
                (content.id, content.alternate_title, content.age, content.import_state),
            )
        else:
            self.db.execute(
                """UPDATE content_items SET title=?,alternate_title=?,format=?,metadata=?,cover=?,backdrop=?,age=?,
                import_state=?,hidden=?,revision=revision+1 WHERE id=?""",
                (
                    content.title,
                    content.alternate_title,
                    content.format,
                    json.dumps(dict(content.metadata), ensure_ascii=False),
                    content.cover,
                    content.backdrop,
                    content.age,
                    content.import_state,
                    int(content.hidden),
                    content.id,
                ),
            )

    def favorites(self, profile_id):
        return {
            r[0]
            for r in self.db.execute("SELECT item_id FROM favorites WHERE profile=?", (profile_id,))
        }

    def favorite(self, profile_id, content_id, value):
        with self.store.transaction():
            if value:
                self.db.execute(
                    "INSERT OR IGNORE INTO favorites(profile,item_id) VALUES(?,?)",
                    (profile_id, content_id),
                )
            else:
                self.db.execute(
                    "DELETE FROM favorites WHERE profile=? AND item_id=?", (profile_id, content_id)
                )

    def activity(self, profile_id):
        rows = self._all(
            "SELECT content_id,event,occurred_at,duration_ms,evidence FROM content_activity WHERE profile_id=?",
            (profile_id,),
        )
        rows += self._all(
            """SELECT game_id AS content_id,status AS event,started_at AS occurred_at,duration_ms,'observed' AS evidence
            FROM play_sessions WHERE profile_id=?""",
            (profile_id,),
        )
        return sorted(rows, key=lambda r: r["occurred_at"], reverse=True)

    def proposal(self, proposal_id):
        return self._one("SELECT * FROM metadata_proposals WHERE id=?", (proposal_id,))
