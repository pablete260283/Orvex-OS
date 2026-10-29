import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest
from orvex.core.installed import InstalledLibrary
from orvex.core.store import Store
from orvex.core.launcher import GameLauncher
from orvex.adapters.dolphin import DolphinAdapter
from orvex.controls.discovery import family, physical_id
from orvex.controls.manager import ControllerManager, engine_for
from real_fixture import build_fixture


class Inventory:
    def __init__(self, devices):
        self.items = devices

    def devices(self):
        return list(self.items)


class ManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.exe = build_fixture(self.root)
        self.emulator = self.root / "dolphin-emu"
        shutil.copy2(self.exe, self.emulator)
        (self.root / "Wii").mkdir()
        (self.root / "Wii" / "Title (USA).rvz").write_bytes(b"test-only")
        self.s = Store(self.root / "test.db")
        self.lib = InstalledLibrary(self.s)
        self.native = self.lib.import_game("Identidad compartida", "PC", str(self.exe))
        adapter = DolphinAdapter(self.s)
        adapter.configure(str(self.emulator), str(self.root))
        adapter.scan()
        self.game = self.s.db.execute("SELECT game_id FROM dolphin_roms").fetchone()[0]
        self.dev = dict(
            name="Nintendo Switch Joy-Con (R)",
            family="joycon-r",
            device_id=physical_id(1, 2, "ABC"),
            stable=True,
        )
        self.inventory = Inventory([self.dev])
        self.m = ControllerManager(self.s, self.lib, self.root / "profiles", self.inventory)

    def tearDown(self):
        self.s.close()
        self.temp.cleanup()

    def profile(self, name="tested", contents=b"[Wiimote1]\nDevice = safe-unit\n"):
        source = self.root / (name + ".ini")
        source.write_bytes(contents)
        return self.m.capture(str(source), name, "dolphin", "joycon-r")

    def test_detect_family_does_not_assume_model_guid_is_unique(self):
        self.assertEqual(family("Nintendo Switch Joy-Con (R)"), "joycon-r")
        self.assertEqual(family("Nintendo Switch Joy-Con (L)"), "joycon-l")
        self.assertEqual(family("DualSense Wireless Controller"), "dualsense")
        self.assertEqual(family("Xbox Controller"), "xbox")
        self.assertEqual(family("Wireless Controller"), "other")
        self.assertEqual(family("Nintendo RVL-CNT-01"), "wiimote")
        self.assertEqual(physical_id(1, 2, ""), "")
        self.assertNotEqual(physical_id(1, 2, "A"), physical_id(1, 2, "B"))

    def test_game_version_engine_and_recent_title_preserved_during_scan(self):
        self.assertEqual(engine_for(self.s, self.native), "native")
        self.assertEqual(engine_for(self.s, self.game), "dolphin")
        row = self.lib.raw(self.game)
        self.lib.edit(self.game, "New Super Mario Bros", "Wii", row["executable"], row["arguments"])
        self.assertEqual(self.lib.raw(self.game)["name"], "New Super Mario Bros")
        DolphinAdapter(self.s).scan()
        self.assertEqual(self.lib.raw(self.game)["name"], "New Super Mario Bros")
        with self.assertRaises(ValueError):
            self.lib.edit(self.game, "x", "Wii", "/wrong", "[]")
        self.s.close()
        self.s = Store(self.root / "test.db")
        self.assertEqual(InstalledLibrary(self.s).raw(self.game)["name"], "New Super Mario Bros")

    def test_hierarchy_players_ambiguity_disconnection_and_restart(self):
        a = self.profile("general")
        b = self.profile("platform")
        c = self.profile("game")
        for p, scope in [(a, "default"), (b, "platform"), (c, "game")]:
            self.m.bind(
                p["id"], scope, self.game, "Wii", "dolphin", self.dev["device_id"], "joycon-r", 1
            )
        self.assertEqual(self.m.select(self.game, [self.dev])[0]["profile"]["id"], c["id"])
        self.assertEqual(self.m.select(self.native, [self.dev]), [])
        self.assertEqual(self.m.select(self.game, []), [])
        self.assertEqual(self.m.select(self.game, [self.dev, self.dev]), [])
        other = dict(self.dev, device_id=physical_id(1, 2, "XYZ"))
        self.m.bind(a["id"], "default", self.game, "", "dolphin", other["device_id"], "joycon-r", 2)
        self.assertEqual([x["player"] for x in self.m.select(self.game, [self.dev, other])], [1, 2])
        self.s.close()
        self.s = Store(self.root / "test.db")
        self.m = ControllerManager(
            self.s, InstalledLibrary(self.s), self.root / "profiles", self.inventory
        )
        self.assertEqual(self.m.select(self.game, [self.dev])[0]["profile"]["id"], c["id"])

    def test_backup_restore_conflict_crash_and_volatile_sdl(self):
        p = self.profile()
        self.m.bind(
            p["id"], "game", self.game, "Wii", "dolphin", self.dev["device_id"], "joycon-r", 1
        )
        target = self.root / "WiimoteNew.ini"
        original = b"[Wiimote1]\nDevice = ORIGINAL\n"
        target.write_bytes(original)
        self.m.configure_target(str(target))
        self.s.set("controller_apply_enabled", True)
        self.m.prepare_for_launch(self.game)
        self.assertEqual(target.read_bytes(), Path(p["snapshot"]).read_bytes())
        journal = self.s.get("controller_restore_journal", {})
        self.assertEqual(Path(journal["backup"]).read_bytes(), original)
        self.m = ControllerManager(self.s, self.lib, self.root / "profiles", self.inventory)
        self.assertEqual(target.read_bytes(), original)
        self.assertFalse(self.s.get("controller_restore_journal", {}))
        self.m.prepare_for_launch(self.game)
        target.write_bytes(b"[Wiimote1]\nDevice = externally edited\n")
        self.assertIn("Recuperación pendiente", self.m.recover())
        self.assertIn(b"externally", target.read_bytes())
        self.assertTrue(Path(self.s.get("controller_restore_journal", {})["backup"]).exists())
        self.s.set("controller_restore_journal", {})
        v = self.profile("volatile", b"[Wiimote1]\nDevice = SDL/0/Nintendo Switch Joy-Con (R)\n")
        self.m.bind(
            v["id"], "game", self.game, "Wii", "dolphin", self.dev["device_id"], "joycon-r", 1
        )
        before = target.read_bytes()
        self.m.prepare_for_launch(self.game)
        self.assertEqual(target.read_bytes(), before)
        self.assertIn("índice SDL variable", self.m.notice)

    def test_actual_process_temporary_profile_and_restore(self):
        p = self.profile()
        self.m.bind(
            p["id"], "game", self.game, "Wii", "dolphin", self.dev["device_id"], "joycon-r", 1
        )
        target = self.root / "WiimoteNew.ini"
        original = b"[Wiimote1]\nDevice = original\n"
        target.write_bytes(original)
        self.m.configure_target(str(target))
        self.s.set("controller_apply_enabled", True)
        launcher = GameLauncher(self.lib)
        launcher.controller_manager = self.m
        launcher.request(self.game)
        self.assertTrue(launcher.pending)
        launcher.confirm()
        deadline = time.monotonic() + 5
        while launcher.busy and time.monotonic() < deadline:
            QTest.qWait(20)
        self.assertFalse(launcher.busy)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(
            self.s.db.execute(
                "SELECT COUNT(*) FROM play_sessions WHERE game_id=?", (self.game,)
            ).fetchone()[0],
            1,
        )

    def test_crash_recovery_waits_for_running_or_unconfirmed_emulator(self):
        p = self.profile()
        self.m.bind(
            p["id"], "game", self.game, "Wii", "dolphin", self.dev["device_id"], "joycon-r", 1
        )
        target = self.root / "WiimoteNew.ini"
        original = b"[Wiimote1]\nDevice = saved\n"
        target.write_bytes(original)
        self.m.configure_target(str(target))
        self.s.set("controller_apply_enabled", True)
        self.m.prepare_for_launch(self.game)
        self.m.mark_starting()
        self.assertIn("podría seguir abierto", self.m.recover())
        self.assertNotEqual(target.read_bytes(), original)
        self.m.mark_running(os.getpid())
        self.assertIn("podría seguir abierto", self.m.recover())
        self.assertNotEqual(target.read_bytes(), original)
        self.assertIn("restaurada", self.m.finish_launch())
        self.assertEqual(target.read_bytes(), original)
