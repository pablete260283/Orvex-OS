import tempfile
import unittest
from pathlib import Path
from orvex.core.store import Store, catalog

class StoreTests(unittest.TestCase):
    def test_roundtrip_across_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"settings.sqlite3"
            s=Store(path); s.set("motion",True); s.close()
            s=Store(path); self.assertIs(s.get("motion"),True); s.close()
    def test_update_and_safe_parameters(self):
        s=Store(":memory:"); s.set("x'; DROP TABLE settings; --",False)
        s.set("x'; DROP TABLE settings; --",True)
        self.assertTrue(s.get("x'; DROP TABLE settings; --")); self.assertEqual(s.get("missing",7),7); s.close()
    def test_demo_catalog(self):
        entries=catalog()
        self.assertTrue({"aurora","orbit","drift","forest","ocean","moon"} <= {e["id"] for e in entries})
        self.assertEqual({e["kind"] for e in entries},{"game","media"})
        self.assertTrue(all((Path(__file__).parents[1]/"src/orvex/ui/assets"/(e["art"]+".svg")).exists() for e in entries))
