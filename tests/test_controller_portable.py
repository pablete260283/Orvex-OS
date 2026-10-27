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
