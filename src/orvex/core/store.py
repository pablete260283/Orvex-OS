"""Preferences, personal library and observed sessions; demo fixtures remain immutable."""
import json
import sqlite3
from pathlib import Path

class Store:
    def __init__(self, path):
        self.path=Path(path) if str(path)!=":memory:" else None
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS favorites (profile TEXT NOT NULL, item_id TEXT NOT NULL, PRIMARY KEY(profile,item_id))")
        self.db.execute("""CREATE TABLE IF NOT EXISTS real_games (
            id TEXT PRIMARY KEY,name TEXT NOT NULL,platform TEXT NOT NULL,executable TEXT NOT NULL UNIQUE,
            trusted_hash TEXT,cover TEXT,backdrop TEXT,created_at TEXT NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS play_sessions (
            id INTEGER PRIMARY KEY,game_id TEXT NOT NULL,started_at TEXT NOT NULL,ended_at TEXT,
            duration_ms INTEGER NOT NULL DEFAULT 0,status TEXT NOT NULL,exit_code INTEGER)""")
        # A previous interrupted host session has no trustworthy end time.
        self.db.execute("UPDATE play_sessions SET status='interrupted' WHERE status='running'")
        self.db.execute("PRAGMA user_version=3")
        self.db.commit()
    def get(self, key, default=None):
        row = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default
    def set(self, key, value):
        with self.db:
            self.db.execute("INSERT INTO settings VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key,json.dumps(value)))
    def favorites(self, profile):
        return [row[0] for row in self.db.execute("SELECT item_id FROM favorites WHERE profile=? ORDER BY item_id",(profile,))]
    def set_favorite(self, profile, item_id, value):
        with self.db:
            if value:
                self.db.execute("INSERT OR IGNORE INTO favorites VALUES (?,?)",(profile,item_id))
            else:
                self.db.execute("DELETE FROM favorites WHERE profile=? AND item_id=?",(profile,item_id))
    def close(self):
        self.db.close()

def catalog():
    from .artwork import resolve_art
    return [dict(e,catalog_source="demo",installed=False,cover_url=resolve_art(e["art"]),backdrop_url=resolve_art(e["art"],"backdrop")) for e in json.loads(Path(__file__).with_name("demo.json").read_text(encoding="utf-8"))]
