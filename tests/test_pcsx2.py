import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from orvex.core.store import Store
from orvex.adapters.pcsx2 import PCSX2Adapter
from orvex.adapters.registry import resolve

class PCSX2Tests(unittest.TestCase):
 def test_index_persist_commands_and_duplicate_feedback(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'PS2').mkdir();rom=root/'PS2'/'My Game.chd';rom.write_bytes(b'unit-test-placeholder')
   s=Store(root/'settings.db');a=PCSX2Adapter(s)
   with patch('orvex.adapters.dolphin.validate_executable',return_value=(str(root/'pcsx2-qt.exe'),'test-hash')):
    a.configure(str(root/'pcsx2-qt.exe'),str(root));self.assertEqual(a.scan(),1);self.assertEqual(a.scan(),0)
    self.assertEqual(a.result,dict(found=1,new=0,existing=1,errors=0))
    key=s.db.execute('SELECT id FROM real_games').fetchone()[0];program,args=resolve(s,key)
    self.assertEqual(args,['-fullscreen','-batch','--',str(rom.resolve())]);self.assertTrue(rom.exists());s.close()
    s=Store(root/'settings.db');self.assertEqual(PCSX2Adapter(s).scan(),0);s.close()
 def test_missing_root_and_file(self):
  s=Store(':memory:');a=PCSX2Adapter(s)
  with self.assertRaises(ValueError):a.scan()
  with patch('orvex.adapters.dolphin.validate_executable',return_value=('pcsx2','hash')):
   with self.assertRaises(OSError):a.command('/missing/file.iso')
  s.close()
