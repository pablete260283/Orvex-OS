"""Immutable domain records and validated source identities."""

import hashlib
import json
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from types import MappingProxyType
from typing import Mapping
from ..core.age_policy import valid_age as valid_age

KINDS = frozenset({"game", "movie", "series", "episode", "application"})
IMPORT_STATES = frozenset({"registered", "available", "missing", "pending"})


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def normalize(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text.casefold()) if unicodedata.category(c) != "Mn"
    )


def source_identity(source_type, reference):
    if not isinstance(source_type, str) or not source_type.strip() or len(source_type) > 100:
        raise ValueError("Tipo de origen no válido.")
    if (
        not isinstance(reference, str)
        or not reference.strip()
        or "\x00" in reference
        or len(reference) > 4096
    ):
        raise ValueError("Origen obligatorio, sin caracteres NUL (máximo 4096).")
    reference = reference.strip()
    if source_type == "local":
        win = PureWindowsPath(reference)
        if win.is_absolute():
            # Windows case-insensitive paths are stable even when tested on Linux.
            from ntpath import normpath

            if sys.platform == "win32":
                # Resolve real filesystem aliases (8.3 paths/junctions) before folding.
                # The legacy scanners already store Path.resolve(), so lexical-only
                # normalization would register the same ROM twice on Windows runners.
                reference = str(Path(reference).resolve(strict=False))
            return "win:" + normpath(reference).replace("\\", "/").casefold()
        path = Path(reference).expanduser()
        if not path.is_absolute():
            raise ValueError("El origen local necesita una ruta absoluta.")
        return "posix:" + str(path.resolve(strict=False))
    return reference


def json_object(value):
    try:
        data = (
            json.loads(value)
            if isinstance(value, str)
            else dict(value)
            if isinstance(value, Mapping)
            else None
        )
        if not isinstance(data, dict):
            raise ValueError()
        json.dumps(data, allow_nan=False)
        return data
    except (TypeError, ValueError):
        raise ValueError("Los metadatos deben ser un objeto JSON válido.") from None


@dataclass(frozen=True)
class Profile:
    id: str
    kind: str
    name: str
    max_age: int | None
    enabled: bool = True


@dataclass(frozen=True)
class Content:
    id: str
    kind: str
    title: str
    alternate_title: str
    format: str
    source_type: str
    source_ref: str
    metadata: Mapping = field(default_factory=dict)
    cover: str | None = None
    backdrop: str | None = None
    age: int | None = None
    import_state: str = "registered"
    hidden: bool = False
    parent_id: str | None = None
    created_at: str = ""
    legacy_game: bool = False

    def __post_init__(self):
        # Deep-copy JSON values; callers cannot mutate persisted data through a record.
        object.__setattr__(
            self, "metadata", MappingProxyType(json_object(json.dumps(dict(self.metadata))))
        )

    @property
    def fingerprint(self):
        data = {key: value for key, value in self.__dict__.items() if key != "metadata"}
        data["metadata"] = dict(self.metadata)
        return hashlib.sha256(
            json.dumps(data, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
        ).hexdigest()


@dataclass(frozen=True)
class Registration:
    content: Content
    created: bool


class ContentUnavailable(LookupError):
    """Not found and not allowed intentionally share the same public error."""


class ProposalConflict(RuntimeError):
    pass
