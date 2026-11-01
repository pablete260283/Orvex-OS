"""Real SQLite migration/backup/restore, with all files confined to TemporaryDirectory."""

import hashlib
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from orvex.core.store import Store, StoreOpenError, MIGRATIONS, SCHEMA_VERSION


class FoundationMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "library.sqlite3"

    def tearDown(self):
        self.temp.cleanup()

    def v5(self):
        with closing(sqlite3.connect(self.path)) as db, db:
            for version in range(1, 6):
                for sql in MIGRATIONS[version]:
                    db.execute(sql)
            db.execute("PRAGMA user_version=5")
            for key, value in [
                ("profile", "adult"),
                ("background_mode", "fixed"),
                ("controller_profiles_v1", [{"id": "real-joycon", "source": "existing-ini"}]),
                ("controller_restore_journal", {"backup": "do not modify"}),
            ]:
                db.execute("INSERT INTO settings VALUES(?,?)", (key, json.dumps(value)))
            db.execute(
                "INSERT INTO real_games(id,name,platform,executable,cover,backdrop,created_at,arguments,trusted_hash,trusted_arguments) VALUES('existing','Existing','Wii','unchanged::existing','cover.png','backdrop.png','2026-01-01','[]','approved','[]')"
            )
            db.execute(
                "INSERT INTO play_sessions(game_id,started_at,status,duration_ms) VALUES('existing','2026-01-01','finished',457800)"
            )
            db.execute("INSERT INTO favorites VALUES('adult','existing')")

    def test_upgrade_preserves_records_and_restore_copy_keeps_v04_schema(self):
        self.v5()
        with closing(sqlite3.connect(self.path)) as original:
            before_dump = list(original.iterdump())
        store = Store(self.path)
        try:
            self.assertEqual(store.db.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
            self.assertEqual(
                store.db.execute(
                    "SELECT id,name,executable,cover,backdrop,trusted_hash FROM real_games"
                ).fetchone(),
                (
                    "existing",
                    "Existing",
                    "unchanged::existing",
                    "cover.png",
                    "backdrop.png",
                    "approved",
                ),
            )
            self.assertEqual(
                store.db.execute("SELECT duration_ms,profile_id FROM play_sessions").fetchone(),
                (457800, None),
            )
            self.assertEqual(store.favorites("adult"), ["existing"])
            self.assertEqual(store.get("controller_profiles_v1")[0]["id"], "real-joycon")
            self.assertEqual(store.get("controller_restore_journal"), {"backup": "do not modify"})
            with closing(sqlite3.connect(store.backup_path)) as snapshot:
                self.assertEqual(list(snapshot.iterdump()), before_dump)
            target = self.path.with_name("restored-for-v04.sqlite3")
            Store.restore_copy(store.backup_path, target)
            with closing(sqlite3.connect(target)) as old:
                self.assertEqual(old.execute("PRAGMA user_version").fetchone()[0], 5)
                self.assertNotIn(
                    "profile_id", {r[1] for r in old.execute("PRAGMA table_info(play_sessions)")}
                )
                self.assertEqual(
                    old.execute("SELECT duration_ms FROM play_sessions").fetchone()[0], 457800
                )
                self.assertEqual(
                    old.execute(
                        "SELECT value FROM settings WHERE key='background_mode'"
                    ).fetchone()[0],
                    '"fixed"',
                )
            with self.assertRaises(FileExistsError):
                Store.restore_copy(store.backup_path, self.path)
        finally:
            store.close()

    def test_failed_v6_rolls_back_entire_schema_and_keeps_original_backup(self):
        self.v5()
        with patch.dict(MIGRATIONS, {6: [*MIGRATIONS[6], "INVALID SQL"]}):
            with self.assertRaises(StoreOpenError):
                Store(self.path)
        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 5)
            self.assertFalse(
                db.execute("SELECT 1 FROM sqlite_master WHERE name='profiles'").fetchone()
            )
            self.assertNotIn(
                "profile_id", {r[1] for r in db.execute("PRAGMA table_info(play_sessions)")}
            )
            self.assertEqual(
                db.execute("SELECT duration_ms FROM play_sessions").fetchone()[0], 457800
            )
        self.assertEqual(len(list(self.path.parent.glob("*.bak"))), 1)

    def test_nested_transactions_snapshot_no_overwrite_and_corruption_rejected(self):
        store = Store(self.path)
        try:
            with self.assertRaises(RuntimeError):
                with store.transaction():
                    store.db.execute("INSERT INTO settings VALUES('outer','1')")
                    with store.transaction():
                        store.db.execute("INSERT INTO settings VALUES('inner','2')")
                    with self.assertRaises(StoreOpenError):
                        store.backup_to(self.path.with_name("unsafe"))
                    raise RuntimeError("abort caller")
            self.assertIsNone(store.get("inner"))
            self.assertIsNone(store.get("outer"))
            with store.transaction():
                store.db.execute("INSERT INTO settings VALUES('outer','1')")
                try:
                    with store.transaction():
                        store.db.execute("INSERT INTO settings VALUES('inner','2')")
                        raise ValueError("abort nested")
                except ValueError:
                    pass
            self.assertEqual(store.get("outer"), 1)
            self.assertIsNone(store.get("inner"))
            copy = store.backup_to(self.path.with_name("snapshot.sqlite3"))
            before = hashlib.sha256(copy.read_bytes()).hexdigest()
            with self.assertRaises(FileExistsError):
                store.backup_to(copy)
            self.assertEqual(hashlib.sha256(copy.read_bytes()).hexdigest(), before)
            corrupt = self.path.with_name("corrupt.bak")
            corrupt.write_bytes(b"broken SQLite")
            with self.assertRaises(sqlite3.DatabaseError):
                Store.restore_copy(corrupt, self.path.with_name("bad-restore"))
            self.assertFalse(self.path.with_name("bad-restore").exists())
            with store.transaction():
                with self.assertRaises(sqlite3.IntegrityError):
                    store.db.execute(
                        "INSERT INTO content_activity VALUES('x','absent','id','opened','2026',NULL,'manual')"
                    )
        finally:
            store.close()

    def test_incoherent_current_schema_is_refused_without_reset(self):
        store = Store(self.path)
        store.close()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("ALTER TABLE content_items RENAME TO preserved_content_items")
            db.execute(
                "CREATE TABLE content_items(id TEXT,kind TEXT,title TEXT,source_key TEXT,parent_id TEXT,revision INTEGER)"
            )
        before = self.path.read_bytes()
        with self.assertRaisesRegex(StoreOpenError, "content_items"):
            Store(self.path)
        self.assertEqual(self.path.read_bytes(), before)

    def test_actual_v04_loader_opens_restored_backup_and_refuses_live_v6(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "orvex_v04_snapshot", Path(__file__).parent / "fixtures/store_v04_snapshot.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.SCHEMA_VERSION, 5)
        self.v5()
        store = Store(self.path)
        backup = store.backup_path
        store.close()
        before = self.path.read_bytes()
        with self.assertRaises(module.StoreOpenError):
            module.Store(self.path)
        self.assertEqual(before, self.path.read_bytes())
        restored = Store.restore_copy(backup, self.path.with_name("actual-v04-restored.sqlite3"))
        old = module.Store(restored)
        try:
            self.assertEqual(old.favorites("adult"), ["existing"])
            self.assertEqual(old.get("controller_profiles_v1")[0]["id"], "real-joycon")
            self.assertEqual(
                old.db.execute("SELECT duration_ms FROM play_sessions").fetchone()[0], 457800
            )
        finally:
            old.close()
