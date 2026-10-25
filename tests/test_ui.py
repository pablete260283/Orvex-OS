import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
os.environ.setdefault("QT_QUICK_BACKEND","software")
import unittest
from pathlib import Path
from PySide6.QtCore import QUrl, Qt, QPoint, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtTest import QTest
from orvex.core.store import Store
from orvex.core.bridge import Bridge

class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QGuiApplication.instance() or QGuiApplication([])
    def setUp(self):
        self.store=Store(":memory:"); self.bridge=Bridge(self.store)
        self.engine=QQmlApplicationEngine(); self.errors=[]
        self.engine.warnings.connect(lambda warnings:self.errors.extend(str(x) for x in warnings))
        self.engine.rootContext().setContextProperty("backend",self.bridge)
        self.engine.load(QUrl.fromLocalFile(str(Path(__file__).parents[1]/"src/orvex/ui/Main.qml")))
        self.assertTrue(self.engine.rootObjects(),"QML failed to load")
        self.window=self.engine.rootObjects()[0]; QTest.qWait(60)
        self.assertEqual(self.window.title(), "ORVEX OS 0.1 · Visual Preview")
    def tearDown(self):
        self.window.close(); del self.window; del self.engine
        self.store.close(); self.assertEqual(self.errors,[])
    def key(self,key):
        QTest.keyClick(self.window,key); self.app.processEvents()
    def test_keyboard_routes_and_back(self):
        for target in [1,2,3,0]:
            self.key(Qt.Key_Right); self.assertEqual(self.window.property("page"),target)
        self.key(Qt.Key_Left); self.key(Qt.Key_Escape)
        self.assertEqual(self.window.property("page"),0)
    def test_content_activation_and_modal_close(self):
        self.key(Qt.Key_Down); self.key(Qt.Key_Right); self.key(Qt.Key_Return)
        self.assertIn("Órbita",self.window.property("notice"))
        self.key(Qt.Key_Right); self.assertIn("Órbita",self.window.property("notice"))
        self.key(Qt.Key_Escape); self.assertEqual(self.window.property("notice"),"")
        self.assertEqual(self.window.property("page"),0)
    def test_settings_persist_through_bridge(self):
        for _ in range(3):self.key(Qt.Key_Right)
        self.key(Qt.Key_Down); self.key(Qt.Key_Return)
        self.assertTrue(self.store.get("reduced_motion"))
    def test_mouse_routes_and_cards(self):
        QTest.mouseClick(self.window,Qt.LeftButton,pos=QPoint(760,65))
        self.assertEqual(self.window.property("page"),2)
        QTest.mouseClick(self.window,Qt.LeftButton,pos=QPoint(150,650))
        self.assertIn("Planeta azul",self.window.property("notice"))
    def test_render_all_pages_at_tv_resolutions(self):
        out=Path(__file__).parents[1]/"preview"; out.mkdir(exist_ok=True)
        for width,height in [(1920,1080),(3840,2160)]:
            self.window.resize(width,height)
            for page,name in enumerate(["home","games","media","settings"]):
                self.window.setProperty("page",page); QTest.qWait(40)
                logo=self.window.findChild(QObject,"brandLogo")
                self.assertIsNotNone(logo)
                self.assertTrue(self.window.property("brandReady"))
                self.assertTrue(logo.property("source").toString().endswith("orvex-horizontal-dark.svg"))
                self.assertAlmostEqual(logo.property("paintedWidth")/logo.property("paintedHeight"),610/165,places=4)
                img=self.window.grabWindow()
                self.assertFalse(img.isNull()); self.assertEqual((img.width(),img.height()),(width,height))
                self.assertTrue(img.save(str(out/(name+("-4k" if width==3840 else "")+".png"))))
