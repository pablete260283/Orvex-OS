"""Existing Qt/native launch path on schema 6. Emulator scans use owned dummy files only."""

import shutil
import sys
import time
import unittest
from PySide6.QtTest import QTest
from orvex.core.store import Store
from orvex.foundation.models import ContentUnavailable
from orvex.foundation.services import FoundationServices
from orvex.ui_runtime import ui_application
from real_fixture import build_fixture
import test_real_ui


class FoundationRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = ui_application()

    setUp = test_real_ui.RealUiTests.setUp
    tearDown = test_real_ui.RealUiTests.tearDown

    def test_confirmed_native_session_has_profile_snapshot_and_survives_restart(self):
        self.exe = build_fixture(self.root, wait_for_release=True)
        self.assertTrue(self.b.importGame("Native foundation integration", "PC", str(self.exe)))
        self.assertEqual(self.b.metaObject().indexOfProperty("foundation"), -1)
        key = self.b.entries[0]["id"]
        self.b.foundation.catalog.favorite(key, "adult", True)
        self.b.refresh()
        self.assertTrue(self.b.entries[0]["favorite"])
        self.b.requestLaunch(key)
        self.assertTrue(self.b.pendingLaunch)
        self.assertFalse((self.exe.parent / "orvex-test-ran.txt").exists())
        self.b.confirmLaunch()
        deadline = time.monotonic() + 3
        while not self.b.launcher.started and time.monotonic() < deadline:
            QTest.qWait(20)
        self.assertTrue(self.b.launchBusy)
        self.b.setProfile("child")
        with self.assertRaises(ContentUnavailable):
            self.b.foundation.catalog.get(key, "child")
        (self.exe.parent / "orvex-test-release.txt").touch()
        deadline = time.monotonic() + 3
        while self.b.launchBusy and time.monotonic() < deadline:
            QTest.qWait(20)
        self.assertFalse(self.b.launchBusy)
        row = self.store.db.execute(
            "SELECT profile_id,status,duration_ms FROM play_sessions"
        ).fetchone()
        self.assertEqual(row[:2], ("adult", "finished"))
        self.assertGreater(row[2], 0)
        self.assertEqual(self.b.foundation.catalog.recent("child"), [])
        reopened = Store(self.root / "test.sqlite3")
        try:
            catalog = FoundationServices(reopened).catalog
            self.assertEqual([c.id for c in catalog.recent("adult")], [key])
            self.assertEqual(catalog.activity("adult")[0]["duration_ms"], row[2])
            self.assertTrue(catalog.get(key, "adult").legacy_game)
            self.assertEqual(catalog.query("child"), [])
        finally:
            reopened.close()

    def test_dolphin_pcsx2_indexed_ids_commands_and_pending_confirmation_unchanged(self):
        for engine, platform in [("dolphin", "Wii"), ("pcsx2", "PS2")]:
            with self.subTest(engine=engine):
                executable = self.root / (engine + (".exe" if sys.platform == "win32" else ""))
                shutil.copy2(self.exe, executable)
                folder = self.root / "ROMs" / platform
                folder.mkdir(parents=True)
                rom = folder / "ORVEX-owned-index-fixture.iso"
                rom.write_bytes(
                    b"ORVEX path-index fixture only; not a commercial game or bootable ROM"
                )
                self.assertTrue(
                    self.b.configureEmulator(engine, str(executable), str(self.root / "ROMs"))
                )
                self.b.scanEmulator(engine)
                key = self.store.db.execute(
                    f"SELECT game_id FROM {engine}_roms WHERE path=?", (str(rom.resolve()),)
                ).fetchone()[0]
                item = self.b.foundation.catalog.get(key, "adult")
                self.assertEqual(item.source_ref, str(rom.resolve()))
                duplicate = self.b.foundation.catalog.register(
                    "adult",
                    kind="game",
                    title="No duplicate",
                    source_type="local",
                    source_ref=str(rom),
                )
                self.assertFalse(duplicate.created)
                self.assertEqual(duplicate.content.id, key)
                expected = getattr(self.b, engine).command(rom)
                self.b.requestLaunch(key)
                self.assertEqual(self.b.pendingLaunch["path"], expected[0])
                import json

                self.assertEqual(json.loads(self.b.pendingLaunch["arguments"]), expected[1])
                self.assertFalse(self.b.launchBusy)
                self.b.cancelLaunch()
                self.assertFalse((self.exe.parent / "orvex-test-ran.txt").exists())
        self.assertEqual(
            self.store.db.execute("SELECT COUNT(*) FROM content_items").fetchone()[0], 0
        )

    def test_new_catalog_entries_do_not_pretend_to_have_a_player_or_game_launcher(self):
        item = self.b.foundation.catalog.register(
            "adult",
            kind="application",
            title="Future app",
            source_type="app-id",
            source_ref="future.application",
        ).content
        with self.assertRaises(ValueError):
            self.b.foundation.games.request(item.id, "adult")
        self.assertFalse(self.b.launchBusy)
        self.assertFalse(self.b.pendingLaunch)

    def test_gui_entrypoint_isolates_foundation_data_in_explicit_directory(self):
        import os
        import subprocess
        from pathlib import Path

        target = self.root / "isolated-foundation"
        env = dict(
            os.environ,
            PYTHONPATH=str(Path(__file__).parents[1] / "src"),
            QT_QPA_PLATFORM="offscreen",
            QT_QUICK_BACKEND="software",
        )
        process = subprocess.Popen(
            [sys.executable, "-m", "orvex", "--data-dir", str(target)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            deadline = time.monotonic() + 8
            while (
                not (target / "preferences.sqlite3").exists()
                and process.poll() is None
                and time.monotonic() < deadline
            ):
                QTest.qWait(30)
            self.assertTrue((target / "preferences.sqlite3").is_file())
            QTest.qWait(500)
            self.assertIsNone(process.poll())
            from contextlib import closing
            import sqlite3

            with closing(sqlite3.connect(target / "preferences.sqlite3")) as db:
                self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 6)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM real_games").fetchone()[0], 0)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM profiles").fetchone()[0], 2)
        finally:
            if process.poll() is None:
                process.terminate()  # only this owned, empty test instance
            _, stderr = process.communicate(timeout=10)
            self.assertNotIn("failed to load", stderr.decode(errors="replace").lower())
