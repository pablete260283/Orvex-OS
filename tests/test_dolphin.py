import tempfile
import unittest
from pathlib import Path
from orvex.core.store import Store
from orvex.adapters.dolphin import DolphinAdapter
from real_fixture import build_fixture

class DolphinTests(unittest.TestCase):
 def test_scan_commands_duplicates_and_persistence_without_boot(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);exe=build_fixture(root);dolphin=exe.with_name('dolphin-emu');exe.rename(dolphin)
   for platform in ['Wii','GameCube']:
    (root/platform).mkdir();(root/platform/'Title with spaces.rvz').write_bytes(b'unit test placeholder, not a ROM')
   s=Store(root/'prefs.sqlite3');a=DolphinAdapter(s);a.configure(str(dolphin),str(root));self.assertIn(str(dolphin),a.detect())
   self.assertEqual(a.scan(),2);self.assertEqual(a.scan(),0);self.assertFalse((dolphin.parent/'orvex-test-ran.txt').exists())
   records=s.db.execute('SELECT id,platform FROM real_games').fetchall();self.assertEqual({e[1] for e in records},{'Wii','GameCube'})
   for key,_ in records:
    program,args=a.resolve_game(key);self.assertEqual(program,str(dolphin));self.assertEqual(args[:2],['--batch','--exec']);self.assertTrue(Path(args[2]).is_file())
   s.close();s=Store(root/'prefs.sqlite3');self.assertEqual(DolphinAdapter(s).scan(),0);s.close()
 def test_missing_paths_and_invalid_configuration(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(':memory:');a=DolphinAdapter(s)
   with self.assertRaises(ValueError):a.scan()
   with self.assertRaises((ValueError,OSError)):a.configure(str(Path(d)/'Dolphin.exe'),d)
   s.close()
