"""Shared age policy, non-destructive migration and launcher argument regressions."""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from orvex.core.bridge import Bridge
from orvex.core.library import LibraryService
from orvex.core.store import MIGRATIONS, Store, StoreOpenError

FIXTURES = Path(__file__).parent / "fixtures"


class PolicyTests(unittest.TestCase):
    def test_shared_age_cases(self):
        store = Store(":memory:")
        service = LibraryService(store)
        for case in json.loads((FIXTURES / "age_policy.json").read_text()):
            with self.subTest(case=case["name"]):
                self.assertEqual(service.allowed(case["entry"], case["profile"]), case["allowed"])
        for age in [float("nan"), float("inf"), 10**1000]:
            self.assertFalse(service.allowed({"age": age}, "child"))
        store.close()

    def test_bridge_and_all_child_surfaces_filter_before_projection(self):
        store = Store(":memory:")
        store.set("library_source", "demo")
        bridge = Bridge(store)
        self.assertFalse(hasattr(bridge, "catalog"))
        self.assertEqual(bridge.metaObject().indexOfProperty("catalog"), -1)
        bridge.service.items = [
            dict(id="allowed", title="Allowed", kind="game", age=7.0, art="aurora", platform="PC"),
            dict(
                id="blocked", title="Blocked", kind="game", age="7", art="drift", platform="Secret"
            ),
        ]
        bridge.setProfile("child")
        self.assertEqual([e["id"] for e in bridge.entries], ["allowed"])
        self.assertEqual([e["id"] for e in bridge.showcase], ["allowed"])
        self.assertNotIn("Secret", bridge.options)
        self.assertNotIn("blocked", [e["id"] for e in bridge.backgroundOptions])
        bridge.focusItem("blocked")
        self.assertEqual(bridge.backgroundArt, "aurora")
        bridge.openTitle("blocked")
        self.assertFalse(bridge.detailOpen)
        bridge.setQuery("Blocked")
        self.assertEqual(bridge.entries, [])
        bridge.setBackgroundMode("fixed")
        store.set("background_fixed", "blocked")
        self.assertEqual(bridge.backgroundUrl, "")
        store.close()


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "prefs.sqlite3"

    def tearDown(self):
        self.temp.cleanup()

    def version3(self):
        with sqlite3.connect(self.path) as db:
            db.executescript((FIXTURES / "schema_v3.sql").read_text())
            db.execute("INSERT INTO settings VALUES ('reduced_motion','true')")
            db.execute(
                "INSERT INTO real_games(id,name,platform,executable,created_at) VALUES('old','Old','PC','/old','2026-01-01')"
            )

    def test_migrations_from_legacy_versions_preserve_preferences(self):
        for version in [0, 1, 2]:
            path = self.path.with_name(f"legacy-{version}.db")
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
                db.execute("INSERT INTO settings VALUES('profile','\"child\"')")
                if version == 2:
                    db.execute(
                        "CREATE TABLE favorites(profile TEXT,item_id TEXT,PRIMARY KEY(profile,item_id))"
                    )
                    db.execute("INSERT INTO favorites VALUES('child','aurora')")
                db.execute(f"PRAGMA user_version={version}")
            store = Store(path)
            self.assertEqual(store.get("profile"), "child")
            self.assertEqual(store.db.execute("PRAGMA user_version").fetchone()[0], 4)
            self.assertTrue(store.backup_path.is_file())
            if version == 2:
                self.assertEqual(store.favorites("child"), ["aurora"])
            store.close()

    def test_v3_upgrade_preserves_games_and_requires_argument_confirmation(self):
        self.version3()
        store = Store(self.path)
        self.assertTrue(store.get("reduced_motion"))
        self.assertEqual(
            store.db.execute("SELECT arguments,trusted_arguments FROM real_games").fetchone(),
            ("[]", None),
        )
        backup = store.backup_path
        store.close()
        with sqlite3.connect(backup) as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 3)
        store = Store(self.path)
        self.assertIsNone(store.backup_path)
        store.close()

    def test_future_version_refused_without_writes_or_downgrade(self):
        with sqlite3.connect(self.path) as db:
            db.execute("PRAGMA user_version=99")
        before = self.path.read_bytes()
        with self.assertRaisesRegex(StoreOpenError, "99"):
            Store(self.path)
        self.assertEqual(self.path.read_bytes(), before)

    def test_corrupt_or_unopenable_database_is_not_replaced(self):
        self.path.write_bytes(b"This is not a SQLite database")
        before = self.path.read_bytes()
        with self.assertRaises(StoreOpenError):
            Store(self.path)
        self.assertEqual(self.path.read_bytes(), before)
        with self.assertRaises(StoreOpenError):
            Store(self.path.parent / "missing" / "prefs.db")

    def test_migration_failure_rolls_back_and_keeps_backup(self):
        self.version3()
        with patch.dict(
            MIGRATIONS, {4: ["ALTER TABLE real_games ADD COLUMN injected TEXT", "INVALID SQL"]}
        ):
            with self.assertRaises(StoreOpenError):
                Store(self.path)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 3)
            self.assertNotIn(
                "injected", [row[1] for row in db.execute("PRAGMA table_info(real_games)")]
            )
        self.assertTrue(list(self.path.parent.glob("*.bak")))

    def test_invalid_preference_defaults_without_overwriting_value(self):
        store = Store(self.path)
        with store.db:
            store.db.execute("INSERT INTO settings VALUES ('profile','invalid json')")
        self.assertEqual(store.get("profile", "adult"), "adult")
        self.assertEqual(
            store.db.execute("SELECT value FROM settings").fetchone()[0], "invalid json"
        )
        self.assertTrue(store.warnings)
        store.close()

    def test_opening_second_connection_does_not_interrupt_live_session(self):
        store = Store(self.path)
        with store.db:
            store.db.execute(
                "INSERT INTO play_sessions(game_id,started_at,status) VALUES('test','2026-01-01','running')"
            )
        other = Store(self.path)
        self.assertEqual(
            other.db.execute("SELECT status FROM play_sessions").fetchone()[0], "running"
        )
        other.close()
        store.recover_sessions()
        self.assertEqual(
            store.db.execute("SELECT status,duration_ms FROM play_sessions").fetchone(),
            ("interrupted", 0),
        )
        store.close()
