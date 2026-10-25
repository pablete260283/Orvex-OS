import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('QT_QUICK_BACKEND','software')
import unittest
from pathlib import Path
from PySide6.QtCore import QUrl,Qt,QPoint,QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtTest import QTest
import shiboken6
from orvex.core.store import Store
from orvex.core.bridge import Bridge

class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QGuiApplication.instance() or QGuiApplication([])
    def setUp(self):
        self.store=Store(':memory:');self.b=Bridge(self.store);self.store.set('reduced_motion',True)
        self.engine=QQmlApplicationEngine();self.errors=[]
        self.engine.warnings.connect(lambda warnings:self.errors.extend(str(x) for x in warnings))
        self.engine.rootContext().setContextProperty('backend',self.b)
        self.engine.load(QUrl.fromLocalFile(str(Path(__file__).parents[1]/'src/orvex/ui/Main.qml')))
        self.assertTrue(self.engine.rootObjects());self.window=self.engine.rootObjects()[0];self.window.requestActivate();QTest.qWait(80)
        self.assertEqual(self.window.title(),'ORVEX OS 0.2 · Visual Preview')
    def tearDown(self):
        self.window.close();shiboken6.delete(self.engine);self.store.close();self.assertEqual(self.errors,[])
    def key(self,key):QTest.keyClick(self.window,key);self.app.processEvents();QTest.qWait(15)
    def click(self,x,y):QTest.mouseClick(self.window,Qt.LeftButton,pos=QPoint(x,y));self.app.processEvents();QTest.qWait(25)
    def test_keyboard_routes_and_back(self):
        for page in [1,2,3,0]:self.key(Qt.Key_Right);self.assertEqual(self.b.page,page)
        self.key(Qt.Key_Left);self.key(Qt.Key_Escape);self.assertEqual(self.b.page,0)
    def test_keyboard_search_open_back_and_state(self):
        self.key(Qt.Key_Right);self.key(Qt.Key_Down);
        for char in 'Aurora':QTest.keyClick(self.window,ord(char),Qt.NoModifier)
        self.app.processEvents()
        self.assertEqual([e['id'] for e in self.b.entries],['aurora'])
        self.key(Qt.Key_Down);self.key(Qt.Key_Return);self.assertTrue(self.b.detailOpen)
        self.key(Qt.Key_Escape);self.assertFalse(self.b.detailOpen);self.assertEqual(self.b.query,'Aurora')
    def test_mouse_routes_open_favorite_demo_and_back(self):
        self.click(760,65);self.assertEqual(self.b.page,2)
        self.click(150,400);self.assertTrue(self.b.detailOpen);self.assertEqual(self.b.detail['id'],'ocean')
        self.click(1100,550);self.assertTrue(self.b.detail['favorite'])
        self.click(750,550);self.assertIn('Demostración',self.window.findChild(QObject,'detailPage').property('notice'))
        self.key(Qt.Key_Escape);self.assertTrue(self.b.detailOpen)
        self.click(140,70);self.assertFalse(self.b.detailOpen)
    def test_mouse_profile_and_settings(self):
        self.b.navigate(2);self.click(1260,65);self.assertEqual(self.b.profile,'child');self.assertTrue(all(e['age']<=7 for e in self.b.entries))
        self.click(920,65);self.assertEqual(self.b.page,3)
        # Interface preference is functional, not a device integration.
        self.click(600,450);self.assertFalse(self.b.reducedMotion)
    def test_render_pages_details_and_child_at_tv_resolutions(self):
        out=Path(__file__).parents[1]/'preview/v0.2';out.mkdir(exist_ok=True)
        for width,height in [(1920,1080),(3840,2160)]:
            self.window.resize(width,height)
            states=[('home',0,'adult',False),('games',1,'adult',False),('media',2,'adult',False),('settings',3,'adult',False),('game-detail',1,'adult',True),('media-detail',2,'adult',True),('child-media',2,'child',False)]
            for name,page,profile,detail in states:
                self.b.setProfile(profile);self.b.navigate(page)
                if detail:self.b.openDetail(0)
                QTest.qWait(45)
                logo=self.window.findChild(QObject,'brandLogo');self.assertTrue(self.window.property('brandReady'))
                self.assertAlmostEqual(logo.property('paintedWidth')/logo.property('paintedHeight'),610/165,places=4)
                img=self.window.grabWindow();self.assertFalse(img.isNull());self.assertEqual((img.width(),img.height()),(width,height))
                self.assertTrue(img.save(str(out/(name+('-4k' if width==3840 else '')+'.png'))))
