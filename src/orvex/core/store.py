"""Preferences, personal library and observed sessions; demo fixtures remain immutable."""

import json
import sqlite3
from pathlib import Path

SCHEMA_VERSION = 5


class StoreOpenError(RuntimeError):
    """Opening failed; the original database is never deleted or replaced."""


MIGRATIONS = {
    5: [
        "ALTER TABLE real_games ADD COLUMN hidden INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE real_games ADD COLUMN metadata TEXT NOT NULL DEFAULT '{}'",
    ],
    1: ["CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)"],
    2: [
        "CREATE TABLE IF NOT EXISTS favorites (profile TEXT NOT NULL, item_id TEXT NOT NULL, PRIMARY KEY(profile,item_id))"
    ],
    3: [
        """CREATE TABLE IF NOT EXISTS real_games (
        id TEXT PRIMARY KEY,name TEXT NOT NULL,platform TEXT NOT NULL,executable TEXT NOT NULL UNIQUE,
        trusted_hash TEXT,cover TEXT,backdrop TEXT,created_at TEXT NOT NULL)""",
        """CREATE TABLE IF NOT EXISTS play_sessions (
        id INTEGER PRIMARY KEY,game_id TEXT NOT NULL,started_at TEXT NOT NULL,ended_at TEXT,
        duration_ms INTEGER NOT NULL DEFAULT 0,status TEXT NOT NULL,exit_code INTEGER)""",
    ],
    4: [
        "ALTER TABLE real_games ADD COLUMN arguments TEXT NOT NULL DEFAULT '[]'",
        "ALTER TABLE real_games ADD COLUMN trusted_arguments TEXT",
    ],
}


class Store:
    def __init__(self, path):
        self.path = Path(path) if str(path) != ":memory:" else None
        self.db = None
        self.backup_path = None
        self.warnings = []
        try:
            self.db = sqlite3.connect(path)
            version = self.db.execute("PRAGMA user_version").fetchone()[0]
            if version > SCHEMA_VERSION:
                raise StoreOpenError(
                    f"Base de datos versión {version}; esta aplicación admite hasta {SCHEMA_VERSION}. Usa una versión más reciente. No se modificaron tus datos."
                )
            if self.db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise StoreOpenError(
                    "SQLite detectó daños. Conserva el archivo y sus copias antes de intentar una recuperación."
                )
            if version < SCHEMA_VERSION and self.path and self.path.stat().st_size:
                import uuid

                self.backup_path = self.path.with_name(
                    self.path.name + f".pre-v{version}-" + uuid.uuid4().hex[:8] + ".bak"
                )
                backup = sqlite3.connect(self.backup_path)
                try:
                    self.db.backup(backup)
                finally:
                    backup.close()
            self.db.execute("BEGIN IMMEDIATE")
            for target in range(version + 1, SCHEMA_VERSION + 1):
                for statement in MIGRATIONS[target]:
                    self.db.execute(statement)
                self.db.execute(f"PRAGMA user_version={target}")
            required = {
                "settings": {"key", "value"},
                "favorites": {"profile", "item_id"},
                "real_games": {
                    "id",
                    "name",
                    "platform",
                    "executable",
                    "trusted_hash",
                    "cover",
                    "backdrop",
                    "created_at",
                    "arguments",
                    "trusted_arguments",
                },
                "play_sessions": {
                    "id",
                    "game_id",
                    "started_at",
                    "ended_at",
                    "duration_ms",
                    "status",
                    "exit_code",
                },
            }
            for table, columns in required.items():
                actual = {row[1] for row in self.db.execute(f"PRAGMA table_info({table})")}
                if not columns <= actual:
                    raise StoreOpenError(
                        "Esquema incoherente: "
                        + table
                        + ". Conserva el archivo; no se reinicializó."
                    )
            self.db.commit()
        except (sqlite3.Error, OSError, StoreOpenError) as error:
            if self.db:
                self.db.rollback()
                self.db.close()
            raise StoreOpenError(f"No se pudo abrir la biblioteca: {error}") from error

    def recover_sessions(self):
        # Only call after acquiring the application's single-instance lock.
        with self.db:
            self.db.execute("UPDATE play_sessions SET status='interrupted' WHERE status='running'")

    def get(self, key, default=None):
        row = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        if not row:
            return default
        try:
            return json.loads(row[0])
        except (ValueError, TypeError):
            self.warnings.append("Preferencia JSON inválida: " + key)
            return default

    def set(self, key, value):
        with self.db:
            self.db.execute(
                "INSERT INTO settings VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, json.dumps(value)),
            )

    def favorites(self, profile):
        return [
            row[0]
            for row in self.db.execute(
                "SELECT item_id FROM favorites WHERE profile=? ORDER BY item_id", (profile,)
            )
        ]

    def set_favorite(self, profile, item_id, value):
        with self.db:
            if value:
                self.db.execute("INSERT OR IGNORE INTO favorites VALUES (?,?)", (profile, item_id))
            else:
                self.db.execute(
                    "DELETE FROM favorites WHERE profile=? AND item_id=?", (profile, item_id)
                )

    def close(self):
        self.db.close()


def catalog():
    from .artwork import resolve_art

    return [
        dict(
            e,
            catalog_source="demo",
            installed=False,
            cover_url=resolve_art(e["art"]),
            backdrop_url=resolve_art(e["art"], "backdrop"),
        )
        for e in json.loads(Path(__file__).with_name("demo.json").read_text(encoding="utf-8"))
    ]
