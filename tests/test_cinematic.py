"""Render actual Qt UI with an imported controlled executable, not commercial games."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('QT_QUICK_BACKEND', 'software')
import shutil
from PySide6.QtCore import Qt, QMetaObject
from PySide6.QtGui import QImage, QColor, QPainter, QLinearGradient
from PySide6.QtTest import QTest
from test_real_ui import RealUiTests
from ui_selectors import find_item
from artifacts import capture_dir

class CinematicTests(RealUiTests):
 def test_posters_real_library_artwork_approval_and_keyboard(self):
  for index in range(6):
   target=self.root/('controlled-'+str(index)+self.exe.suffix);shutil.copy2(self.exe,target)
   self.b.importGame('Aplicación controlada '+str(index+1),'PC Linux',str(target))
  ids=[e['id'] for e in self.b.showcase]
  image=QImage(1200,1800,QImage.Format_RGB32)
  for index,key in enumerate(ids):
   image.fill(QColor(['#174653','#583c52','#254839'][index%3]))
   painter=QPainter(image);painter.setPen(QColor('#c9eeeb'));font=painter.font();font.setPixelSize(90);painter.setFont(font)
   painter.drawText(image.rect(),Qt.AlignCenter,'ORVEX\nPRUEBA\n'+str(index+1));painter.end()
   source=self.root/('poster'+str(index)+'.png');image.save(str(source))
   self.b.prepareArtwork(key,'cover',str(source));self.assertFalse(self.b.installed.raw(key)['cover']);self.b.confirmArtwork()
  background=QImage(1920,1080,QImage.Format_RGB32);painter=QPainter(background)
  gradient=QLinearGradient(0,0,1920,1080);gradient.setColorAt(0,QColor('#09252d'));gradient.setColorAt(.65,QColor('#32666b'));gradient.setColorAt(1,QColor('#111e26'));painter.fillRect(background.rect(),gradient)
  painter.setBrush(QColor('#487c80'));painter.setPen(Qt.NoPen);painter.drawEllipse(1200,100,550,550);painter.end()
  source=self.root/'background.png';background.save(str(source))
  self.b.prepareArtwork(ids[0],'backdrop',str(source));self.b.confirmArtwork();self.b.focusItem(ids[0])
  page=find_item(self.window,'consolePage');QMetaObject.invokeMethod(page,'enter');QTest.qWait(400)
  poster=find_item(self.window,'recent-'+ids[0]);self.assertAlmostEqual(poster.width()/poster.height(),2/3)
  self.assertEqual(self.b.featured['id'],ids[0]);self.assertTrue(self.b.backgroundUrl.startswith('file:'))
  QTest.keyClick(self.window,Qt.Key_Right);QTest.qWait(50);self.assertEqual(self.b.featured['id'],ids[1])
  QTest.keyClick(self.window,Qt.Key_Left);QTest.qWait(400)
  out=capture_dir('cinematic')
  for width,height in [(1920,1080),(3840,2160)]:
   self.window.resize(width,height);QTest.qWait(300);self.assertTrue(self.window.grabWindow().save(str(out/('native-'+str(width)+'.png'))))
  QTest.keyClick(self.window,Qt.Key_Return);QTest.qWait(50);self.assertTrue(self.b.detailOpen)
  QTest.keyClick(self.window,Qt.Key_Escape);QTest.qWait(50);self.assertFalse(self.b.detailOpen)
