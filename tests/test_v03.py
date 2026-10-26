import tempfile
import unittest
from pathlib import Path
from orvex.core.store import Store
from orvex.core.installed import InstalledLibrary
from orvex.core.metadata_local import LocalMetadata
from real_fixture import build_fixture

class ManagementTests(unittest.TestCase):
 def test_hide_edit_remove_preserves_files_and_optional_history(self):
  with tempfile.TemporaryDirectory() as d:
   exe=build_fixture(Path(d));s=Store(':memory:');lib=InstalledLibrary(s)
   key=lib.import_game('Test','Linux',str(exe))
   lib.hide(key,True);self.assertEqual(lib.games(),[]);self.assertEqual(len(lib.games('adult',True)),1)
   lib.edit(key,'Edited','Linux',str(exe),'[]');self.assertEqual(lib.raw(key)['name'],'Edited')
   with s.db:s.db.execute("INSERT INTO play_sessions(game_id,started_at,status) VALUES(?,'2026','finished')",(key,))
   lib.remove(key,True);self.assertTrue(exe.exists());self.assertEqual(s.db.execute('SELECT COUNT(*) FROM play_sessions').fetchone()[0],1);s.close()
 def test_metadata_requires_explicit_confirmation(self):
  with tempfile.TemporaryDirectory() as d:
   exe=build_fixture(Path(d));s=Store(':memory:');lib=InstalledLibrary(s);key=lib.import_game('Test','Linux',str(exe));provider=LocalMetadata(lib)
   provider.propose(key,'{"description":"Local approved description","edition":"Test"}')
   self.assertEqual(lib.raw(key)['metadata'],'{}');provider.confirm();self.assertIn('approved',lib.raw(key)['metadata']);s.close()
