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
from artifacts import capture_dir
from ui_selectors import find_item
from orvex.core.store import Store
from orvex.core.bridge import Bridge

class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QGuiApplication.instance() or QGuiApplication([])
    def setUp(self):
        self.store=Store(':memory:');self.store.set("library_source","demo");self.b=Bridge(self.store);self.store.set('reduced_motion',True)
        self.engine=QQmlApplicationEngine();self.errors=[]
        self.engine.warnings.connect(lambda warnings:self.errors.extend(str(x) for x in warnings))
        self.engine.rootContext().setContextProperty('backend',self.b)
        self.engine.load(QUrl.fromLocalFile(str(Path(__file__).parents[1]/'src/orvex/ui/Main.qml')))
        self.assertTrue(self.engine.rootObjects());self.window=self.engine.rootObjects()[0];self.window.requestActivate();QTest.qWait(80)
        self.assertEqual(self.window.title(),'ORVEX OS 0.2 · Biblioteca local')
    def tearDown(self):
        self.window.close();shiboken6.delete(self.engine);self.store.close();self.assertEqual(self.errors,[])
    def key(self,key):QTest.keyClick(self.window,key);self.app.processEvents();QTest.qWait(15)
    def click(self,x,y):QTest.mouseClick(self.window,Qt.LeftButton,pos=QPoint(x,y));self.app.processEvents();QTest.qWait(25)
    def test_featured_background_updates_on_focus(self):
        self.b.focusItem('orbit');QTest.qWait(40)
        self.assertEqual(self.window.findChild(QObject,'heroTitle').property('text'),'Órbita')
        self.assertEqual(self.b.backgroundArt,'orbit')
    def itemclick(self,name):
        item=find_item(self.window,name);pt=item.mapToScene(item.boundingRect().center());self.click(round(pt.x()),round(pt.y()))
    def showlibrary(self):
        self.window.findChild(QObject,'consolePage').setProperty('fromLibrary',True)
        self.window.findChild(QObject,'consolePage').metaObject()
        from PySide6.QtCore import QMetaObject
        QMetaObject.invokeMethod(self.window.findChild(QObject,'consolePage'),'restore');QTest.qWait(30)
    def test_keyboard_routes_and_back(self):
        self.assertEqual(self.b.page,1)
        self.key(Qt.Key_Right);self.assertEqual(self.b.page,2)
        self.key(Qt.Key_Left);self.assertEqual(self.b.page,1)
        self.itemclick('settingsButton');self.assertEqual(self.b.page,3)
        self.key(Qt.Key_Escape);self.assertEqual(self.b.page,1)
    def test_keyboard_search_open_back_and_state(self):
        self.showlibrary();search=self.window.findChild(QObject,'librarySearch');search.forceActiveFocus()
        for char in 'Aurora':QTest.keyClick(self.window,ord(char),Qt.NoModifier)
        self.app.processEvents();self.assertEqual([e['id'] for e in self.b.entries],['aurora'])
        self.key(Qt.Key_Down);self.key(Qt.Key_Return);self.assertTrue(self.b.detailOpen)
        self.key(Qt.Key_Escape);self.assertFalse(self.b.detailOpen);self.assertEqual(self.b.query,'Aurora')
        self.assertEqual(self.window.activeFocusItem().property('entry').toVariant()['id'],'aurora')
    def test_mouse_routes_open_favorite_demo_and_back(self):
        self.itemclick('nav2');self.assertEqual(self.b.page,2)
        self.itemclick('recent-ocean');self.assertTrue(self.b.detailOpen);self.assertEqual(self.b.detail['id'],'ocean')
        self.itemclick('detailFavorite');self.assertTrue(self.b.detail['favorite'])
        self.itemclick('demoPlay');self.assertIn('Demostración',self.window.findChild(QObject,'detailPage').property('notice'))
        self.key(Qt.Key_Escape);self.assertTrue(self.b.detailOpen)
        self.itemclick('detailBack');self.assertFalse(self.b.detailOpen)
    def test_favorite_keeps_selected_card_on_return(self):
        self.showlibrary();self.b.selectIndex(1);self.b.openDetail(1);QTest.qWait(30)
        self.b.toggleFavorite('orbit');QTest.qWait(30);self.b.closeDetail();QTest.qWait(30)
        self.assertEqual(self.b.selectedIndex,1)
        self.assertEqual(self.window.activeFocusItem().property('entry').toVariant()['id'],'orbit')
    def test_mouse_filter_popup_and_empty_favorites(self):
        self.showlibrary();self.itemclick('libraryFilter');self.key(Qt.Key_End);self.key(Qt.Key_Return)
        self.assertEqual(self.b.category,'PC');self.assertEqual(len(self.b.entries),2)
        self.itemclick('favoritesFilter');self.assertTrue(self.b.favoritesOnly);self.assertEqual(self.b.entries,[])
        self.b.clearFilters();self.assertFalse(self.b.favoritesOnly);self.assertEqual(self.b.category,'Todas')
    def test_mouse_profile_and_settings(self):
        self.b.navigate(2);self.itemclick('profileButton');QTest.qWait(100);self.itemclick('childProfileChoice')
        # Explicit popup choice is exercised by click, not an automatic profile toggle.
        self.assertEqual(self.b.profile,'child');self.assertTrue(all(e['age']<=7 for e in self.b.showcase))
        self.key(Qt.Key_Escape);self.itemclick('settingsButton');self.assertEqual(self.b.page,3)
        self.itemclick('reducedMotion');self.assertFalse(self.b.reducedMotion)
    def test_render_pages_details_and_child_at_tv_resolutions(self):
        out=capture_dir('qt-demo');out.mkdir(exist_ok=True)
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

            self.b.setProfile('adult');self.b.navigate(1);self.showlibrary();QTest.qWait(50)
            self.assertTrue(self.window.grabWindow().save(str(out/('library'+('-4k' if width==3840 else '')+'.png'))))
