from orvex.ui_runtime import ui_application
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('QT_QUICK_BACKEND','software')
import tempfile,time,unittest
from pathlib import Path
from PySide6.QtCore import QObject,QUrl,Qt,QPoint,QMetaObject
from PySide6.QtGui import QImage,QColor
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem,QQuickWindow
from PySide6.QtTest import QTest
import shiboken6
from artifacts import capture_dir
from ui_selectors import find_item
from orvex.core.store import Store
from orvex.core.bridge import Bridge
from real_fixture import build_fixture
class RealUiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=ui_application()
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.exe=build_fixture(self.root)
  self.store=Store(self.root/'test.sqlite3');self.b=Bridge(self.store);self.store.set('reduced_motion',True)
  self.errors=[];self.engine=QQmlApplicationEngine();self.engine.warnings.connect(lambda w:self.errors.extend(str(x) for x in w))
  self.engine.rootContext().setContextProperty('backend',self.b);self.engine.load(QUrl.fromLocalFile(str(Path(__file__).parents[1]/'src/orvex/ui/Main.qml')))
  self.assertTrue(self.engine.rootObjects());self.window=self.engine.rootObjects()[0];self.window.resize(1920,1080);self.window.requestActivate();QTest.qWait(80)
 def tearDown(self):
  (self.exe.parent/"orvex-test-release.txt").touch()
  deadline=time.monotonic()+5
  while self.b.launchBusy and time.monotonic()<deadline:QTest.qWait(20)
  self.assertFalse(self.b.launchBusy);self.b.cancelLaunch();self.b.cancelArtwork();self.window.close();shiboken6.delete(self.engine);self.store.close();self.temp.cleanup();self.assertEqual(self.errors,[])
 def click(self,name):
  item=find_item(self.window,name);p=item.mapToScene(item.boundingRect().center());QTest.mouseClick(self.window,Qt.LeftButton,pos=QPoint(round(p.x()),round(p.y())));QTest.qWait(40)
 def import_form(self):
  QMetaObject.invokeMethod(self.window,'openImport');QTest.qWait(100)
  for name,text in [('importName','ORVEX · Aplicación controlada'),('importPlatform','PC Linux'),('importExecutable',str(self.exe))]:self.window.findChild(QObject,name).setProperty('text',text)
  self.click('importSave');self.assertEqual(len(self.b.entries),1);self.assertFalse((self.exe.parent/'orvex-test-ran.txt').exists())
 def test_real_ui_import_confirm_launch_and_observed_statistics(self):
  self.exe=build_fixture(self.root,wait_for_release=True)
  self.import_form();game_id=self.b.entries[0]['id'];self.b.openTitle(game_id);QTest.qWait(40);self.click('demoPlay');self.assertTrue(self.b.pendingLaunch);self.assertFalse(self.b.launchBusy)
  QTest.qWait(100);QTest.keyClick(self.window,Qt.Key_Escape);QTest.qWait(30);self.assertFalse(self.b.pendingLaunch);self.assertFalse(self.b.launchBusy);self.click('demoPlay');QTest.qWait(100);self.assertEqual(self.window.activeFocusItem().objectName(),'cancelLaunch');QTest.keyClick(self.window,Qt.Key_Left);self.assertEqual(self.window.activeFocusItem().objectName(),'confirmLaunch');QTest.keyClick(self.window,Qt.Key_Return);QTest.qWait(20);self.assertTrue(self.b.launchBusy);self.assertFalse(self.window.close());self.assertTrue(self.window.isVisible())
  (self.exe.parent/"orvex-test-release.txt").touch()
  deadline=time.monotonic()+5
  while self.b.launchBusy and time.monotonic()<deadline:QTest.qWait(20)
  self.assertFalse(self.b.launchBusy);self.assertTrue((self.exe.parent/'orvex-test-ran.txt').exists());self.assertIsNotNone(self.b.detail['progress']['last_session']);self.assertIsNone(self.b.detail['progress']['percent'])
 def test_capture_real_empty_import_confirmation_and_session_at_tv_resolutions(self):
  out=capture_dir('qt-real');out.mkdir(exist_ok=True)
  def snap(name):QTest.qWait(50);self.assertTrue(self.window.grabWindow().save(str(out/(name+'.png'))))
  snap('empty');QMetaObject.invokeMethod(self.window,'openImport');QTest.qWait(100);snap('import')
  for name,text in [('importName','ORVEX · Aplicación controlada'),('importPlatform','PC Linux'),('importExecutable',str(self.exe))]:self.window.findChild(QObject,name).setProperty('text',text)
  self.click('importSave');self.b.openTitle(self.b.entries[0]['id']);self.b.requestLaunch(self.b.detail['id']);QTest.qWait(100);snap('confirmation');self.b.cancelLaunch();self.b.closeDetail()
  self.b.requestLaunch(self.b.entries[0]['id']);self.b.confirmLaunch()
  deadline=time.monotonic()+5
  while self.b.launchBusy and time.monotonic()<deadline:QTest.qWait(20)
  snap('observed')
  image=QImage(1280,720,QImage.Format_RGB32);image.fill(QColor('#084c61'));source=self.root/'personal-background.png';image.save(str(source))
  self.b.prepareArtwork(self.b.entries[0]['id'],'backdrop',str(source));QTest.qWait(100);snap('artwork-confirmation');self.click('confirmArtwork');self.assertIn('artwork',self.b.backgroundUrl);snap('personal-background')
  self.window.resize(3840,2160);snap('observed-4k');self.b.openTitle(self.b.entries[0]['id']);snap('detail-4k')
  self.window.resize(1920,1080);snap('detail')
