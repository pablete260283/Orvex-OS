import os,sys
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('QT_QUICK_BACKEND','software')
import tempfile,time,unittest
from pathlib import Path
from PySide6.QtGui import QGuiApplication,QImage,QColor
from PySide6.QtTest import QTest
from orvex.core.store import Store
from orvex.core.bridge import Bridge
from orvex.core.installed import validate_executable
from real_fixture import build_fixture

class RealLaunchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QGuiApplication.instance() or QGuiApplication([])
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.exe=build_fixture(self.root)
  self.store=Store(self.root/'prefs.sqlite3');self.b=Bridge(self.store)
 def tearDown(self):
  self.assertFalse(self.b.launchBusy);self.b.cancelArtwork();self.store.close();self.temp.cleanup()
 def imported(self):
  self.assertTrue(self.b.importGame('Aplicación controlada','PC Linux',str(self.exe)));return next(e['id'] for e in self.b.entries if e['availability']==str(self.exe))
 def wait_finished(self):
  deadline=time.monotonic()+5
  while self.b.launchBusy and time.monotonic()<deadline:QTest.qWait(20)
  self.assertFalse(self.b.launchBusy)
 def test_import_does_not_execute_and_persists(self):
  self.assertEqual(self.b.librarySource,'real');self.assertEqual(self.b.entries,[])
  game_id=self.imported();self.assertFalse((self.exe.parent/'orvex-test-ran.txt').exists());self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM play_sessions').fetchone()[0],0)
  self.store.set('reduced_motion',True);self.store.close();self.store=Store(self.root/'prefs.sqlite3');self.b=Bridge(self.store)
  self.assertEqual(self.b.entries[0]['id'],game_id);self.assertTrue(self.b.reducedMotion);self.assertIsNone(self.b.entries[0]['progress']['percent'])
 def test_confirm_launch_finish_time_and_repeat(self):
  game_id=self.imported();self.b.requestLaunch(game_id);self.assertTrue(self.b.pendingLaunch);self.assertFalse(self.b.launchBusy)
  self.b.confirmLaunch();self.assertTrue(self.b.launchBusy);self.wait_finished()
  self.assertTrue((self.exe.parent/'orvex-test-ran.txt').exists())
  row=self.store.db.execute('SELECT duration_ms,status,exit_code FROM play_sessions').fetchone();self.assertGreaterEqual(row[0],200);self.assertEqual(row[1:],('finished',0))
  self.assertIsNotNone(self.b.entries[0]['progress']['last_session']);self.assertEqual(self.b.entries[0]['progress']['source'],'observed')
  self.b.requestLaunch(game_id);self.assertFalse(self.b.pendingLaunch);self.wait_finished();self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM play_sessions').fetchone()[0],2)
  self.store.close();self.store=Store(self.root/'prefs.sqlite3');self.b=Bridge(self.store);self.assertGreaterEqual(self.store.db.execute('SELECT SUM(duration_ms) FROM play_sessions').fetchone()[0],400);self.assertIsNotNone(self.b.entries[0]['progress']['last_session'])
 def test_cancel_then_changed_binary_requires_new_confirmation(self):
  game_id=self.imported();self.b.requestLaunch(game_id);self.b.cancelLaunch();self.b.confirmLaunch();self.assertFalse(self.b.launchBusy)
  self.b.requestLaunch(game_id)
  with self.exe.open('ab') as f:f.write(b'changed')
  self.b.confirmLaunch();self.assertFalse(self.b.launchBusy);self.assertIn('cambió',self.b.operationMessage)
  self.b.requestLaunch(game_id);self.b.confirmLaunch();self.wait_finished()
  with self.exe.open('ab') as f:f.write(b'changed again')
  self.b.requestLaunch(game_id);self.assertTrue(self.b.pendingLaunch);self.b.cancelLaunch()
 def test_invalid_paths_duplicate_and_no_shell_import(self):
  for path in ['relative/path',str(self.root),str(self.root/'missing'),'https://example.com/a.exe']:
   self.assertFalse(self.b.importGame('test','PC',path))
  script=self.root/'script';script.write_text('#!/bin/sh\ntouch DO_NOT_RUN\n');script.chmod(0o755)
  self.assertFalse(self.b.importGame('script','PC',str(script)));self.imported();self.assertFalse(self.b.importGame('duplicate','PC',str(self.exe)))
  self.assertEqual(len(self.b.entries),1)
 def test_failed_start_and_nonzero_exit(self):
  bad=self.root/('invalid-native.exe' if sys.platform=='win32' else 'invalid-elf');bad.write_bytes(b'MZinvalid' if sys.platform=='win32' else b'\x7fELFinvalid');bad.chmod(0o755)
  self.assertTrue(self.b.importGame('invalid','Linux',str(bad)));game_id=self.b.entries[0]['id'];self.b.requestLaunch(game_id);self.b.confirmLaunch();self.wait_finished()
  self.assertIn('No se pudo iniciar',self.b.operationMessage);self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM play_sessions').fetchone()[0],0)
  build_fixture(self.root,7);game_id=self.imported();self.b.requestLaunch(game_id);self.b.confirmLaunch();self.wait_finished();self.assertEqual(self.store.db.execute('SELECT status,exit_code FROM play_sessions').fetchone(),('error',7))
 def test_child_demo_separation_and_pending_authorization(self):
  game_id=self.imported();self.b.requestLaunch(game_id);self.b.setProfile('child');self.b.confirmLaunch();self.assertFalse(self.b.launchBusy);self.assertEqual(self.b.entries,[]);self.assertEqual(self.b.showcase,[])
  self.b.setProfile('adult');self.b.setLibrarySource('demo');self.assertTrue(all(not e.get('installed') for e in self.b.entries));self.b.requestLaunch(game_id);self.assertFalse(self.b.launchBusy)
 def test_missing_executable_after_import_and_running_busy(self):
  game_id=self.imported();self.b.requestLaunch(game_id);self.b.confirmLaunch();self.b.requestLaunch(game_id);self.assertIn('Ya hay',self.b.operationMessage);self.wait_finished()
  self.exe.unlink();self.b.requestLaunch(game_id);self.assertFalse(self.b.launchBusy);self.assertFalse(self.b.pendingLaunch)
 def test_artwork_preview_confirmation_replacement_and_persistence(self):
  game_id=self.imported();source=self.root/'art.png';image=QImage(120,80,QImage.Format_RGB32);image.fill(QColor('#126b62'));self.assertTrue(image.save(str(source)))
  self.assertTrue(self.b.prepareArtwork(game_id,'cover',str(source)));self.assertIsNone(self.b.installed.raw(game_id)['cover']);staged=self.b.pendingArtwork['staged'];self.b.cancelArtwork();self.assertFalse(Path(staged).exists())
  self.b.prepareArtwork(game_id,'cover',str(source));self.b.confirmArtwork();first=self.b.installed.raw(game_id)['cover'];self.assertTrue(Path(first).exists());self.assertIn('file:',self.b.entries[0]['cover_url'])
  self.b.prepareArtwork(game_id,'cover',str(source));self.assertTrue(self.b.pendingArtwork['replacing']);self.b.confirmArtwork();self.assertFalse(Path(first).exists())
  self.b.prepareArtwork(game_id,'backdrop',str(source));self.b.confirmArtwork();self.assertEqual(self.b.backgroundUrl,self.b.entries[0]['backdrop_url'])
  self.assertFalse(self.b.prepareArtwork(game_id,'cover',str(self.exe)));self.assertFalse(self.b.prepareArtwork(game_id,'unknown',str(source)))
  self.store.close();self.store=Store(self.root/'prefs.sqlite3');self.b=Bridge(self.store);self.assertTrue(Path(self.b.installed.raw(game_id)['cover']).exists())
 def test_interrupted_session_recovery_does_not_invent_duration(self):
  game_id=self.imported()
  with self.store.db:self.store.db.execute("INSERT INTO play_sessions(game_id,started_at,status) VALUES(?,'2026-01-01','running')",(game_id,))
  self.store.close();self.store=Store(self.root/'prefs.sqlite3');self.store.recover_sessions();self.b=Bridge(self.store)
  self.assertEqual(self.store.db.execute('SELECT status,duration_ms,ended_at FROM play_sessions').fetchone(),('interrupted',0,None))

 def test_arguments_are_literal_persisted_confirmed_and_states_observable(self):
  import json
  args=['--fullscreen','two words','$(touch MUST_NOT_EXIST)','a&b']
  self.assertTrue(self.b.importGame('Arguments','Linux',str(self.exe),json.dumps(args)))
  game_id=self.b.entries[0]['id'];states=[]
  self.b.launcher.changed.connect(lambda:states.append(self.b.launchState))
  self.assertEqual(self.b.launchState,'Disponible');self.b.requestLaunch(game_id)
  self.assertEqual(self.b.launchState,'Preparando');self.assertEqual(json.loads(self.b.pendingLaunch['arguments']),args)
  self.b.confirmLaunch();self.wait_finished()
  self.assertIn('Ejecutando',states);self.assertEqual(self.b.launchState,'Finalizado')
  self.assertEqual((self.exe.parent/'orvex-test-args.txt').read_text().splitlines(),args)
  self.assertFalse((self.exe.parent/'MUST_NOT_EXIST').exists())
  with self.store.db:self.store.db.execute("UPDATE real_games SET arguments=? WHERE id=?",('["changed"]',game_id))
  self.b.requestLaunch(game_id);self.assertTrue(self.b.pendingLaunch)
  with self.store.db:self.store.db.execute("UPDATE real_games SET arguments=? WHERE id=?",('["changed again"]',game_id))
  self.b.confirmLaunch();self.assertEqual(self.b.launchState,'Error');self.assertFalse(self.b.launchBusy)
  self.b.requestLaunch(game_id);self.b.cancelLaunch();self.assertEqual(self.b.launchState,'Disponible')
  self.store.close();self.store=Store(self.root/'prefs.sqlite3');self.b=Bridge(self.store)
  self.assertEqual(self.b.installed.raw(game_id)['arguments'],'["changed again"]')
 def test_invalid_arguments_rejected_without_import(self):
  for value in ['--not-json','{}','[1]','[null]','["\\u0000"]']:
   self.assertFalse(self.b.importGame('Invalid','PC',str(self.exe),value))
  self.assertEqual(self.b.entries,[])
