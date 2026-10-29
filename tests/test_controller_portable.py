"""Pure SQLite/profile tests that do not need a Linux compiler or physical pad."""

import tempfile
import unittest
from pathlib import Path
from orvex.controls.manager import ControllerManager
from orvex.core.installed import InstalledLibrary
from orvex.core.store import Store


class PortableTests(unittest.TestCase):
    def test_profile_selection_persistence_and_backups(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            store = Store(root / "portable.sqlite")
            store.db.execute(
                "INSERT INTO real_games(id,name,platform,executable,created_at) VALUES('local-test','Game','PC','placeholder','2026')"
            )
            store.db.commit()
            manager = ControllerManager(store, InstalledLibrary(store), root / "profiles", None)
            source = root / "approved.ini"
            source.write_text("[Profile]\nButton=A\n", encoding="utf-8")
            profile = manager.capture(str(source), "Personal", "native", "xbox")
            manager.bind(
                profile["id"], "game", "local-test", "PC", "native", "stable-id", "xbox", 1
            )
            dev = dict(family="xbox", device_id="stable-id", stable=True, backend="SDL")
            self.assertEqual(manager.select("local-test", [dev])[0]["profile"]["id"], profile["id"])
            duplicate = dict(family="xbox", device_id="", stable=False, backend="XInput")
            self.assertEqual(manager.select("local-test", [dev, duplicate]), [])
            self.assertEqual(source.read_text(encoding="utf-8"), "[Profile]\nButton=A\n")
            store.close()
            store = Store(root / "portable.sqlite")
            manager = ControllerManager(store, InstalledLibrary(store), root / "profiles", None)
            self.assertEqual(manager.select("local-test", [dev])[0]["profile"]["id"], profile["id"])
            store.close()


class RecoveryOwnershipTests(unittest.TestCase):
    def test_other_launch_and_manual_retry_never_restore_a_running_session(self):
        import os
        from orvex.core.launcher import GameLauncher

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            store = Store(root / "prefs.sqlite3")
            library = InstalledLibrary(store)
            store.db.execute(
                "INSERT INTO real_games(id,name,platform,executable,created_at) VALUES('local-wii','Game','Wii','placeholder','2026')"
            )
            store.db.execute("CREATE TABLE dolphin_roms(game_id TEXT PRIMARY KEY,path TEXT)")
            store.db.execute("INSERT INTO dolphin_roms VALUES('local-wii','test.rvz')")
            store.db.commit()
            owner = ControllerManager(store, library, root / "profiles", None)
            source = root / "source.ini"
            source.write_bytes(b"[Wiimote1]\nDevice=unit-test\n")
            profile = owner.capture(str(source), "Approved", "dolphin", "joycon-r")
            target = root / "WiimoteNew.ini"
            original = b"[Wiimote1]\nDevice=original\n"
            target.write_bytes(original)
            owner.configure_target(str(target))
            store.set("controller_apply_enabled", True)
            self.assertTrue(owner.apply_for_launch("local-wii", [dict(player=1, profile=profile)]))
            owner.mark_starting()
            owner.mark_running(os.getpid())
            journal = store.get("controller_restore_journal", {})
            applied = target.read_bytes()
            other = ControllerManager(store, library, root / "profiles", None)
            self.assertIn("podría seguir abierto", other.recovery)
            other.mark_starting()
            other.mark_running(99999999)
            self.assertEqual(store.get("controller_restore_journal", {}), journal)
            launcher = GameLauncher(library)
            launcher.controller_manager = other
            launcher._release()
            self.assertEqual(target.read_bytes(), applied)
            self.assertEqual(store.get("controller_restore_journal", {}), journal)
            self.assertIn("podría seguir abierto", other.recover(confirmed_stopped=True))
            self.assertIn("otro lanzamiento", other.recover(finished_transaction="wrong-token"))
            self.assertEqual(target.read_bytes(), applied)
            self.assertIn("restaurada", owner.finish_launch())
            self.assertEqual(target.read_bytes(), original)
            self.assertFalse(store.get("controller_restore_journal", {}))
            store.close()
