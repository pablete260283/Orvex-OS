import unittest,tempfile
from pathlib import Path
from orvex.core.store import Store
from orvex.core.bridge import Bridge
from orvex.core.progress import DemoProgressProvider
class VisualTests(unittest.TestCase):
 def setUp(self):self.s=Store(':memory:');self.s.set("library_source","demo");self.b=Bridge(self.s)
 def tearDown(self):self.s.close()
 def test_recent_games_and_unknown_percentage(self):
  self.assertEqual([e['id'] for e in self.b.recentGames],['aurora','orbit','drift'])
  self.b.focusItem('orbit');self.assertEqual(self.b.backgroundArt,'orbit');self.assertEqual(self.b.featured['progress']['percentLabel'],'Sin porcentaje disponible')
  self.b.navigate(1);self.b.openDetail(3);self.assertEqual(self.b.detail['progress']['statusLabel'],'No iniciado')
 def test_background_modes_and_persistence(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/'prefs.db');b=Bridge(s);b.setBackgroundMode('fixed');b.setFixedBackground('moon');s.close()
   s=Store(Path(d)/'prefs.db');b=Bridge(s);self.assertEqual(b.backgroundArt,'moon');self.assertEqual(b.backgroundMode,'fixed');b.setBackgroundMode('default');self.assertEqual(b.backgroundArt,'');s.close()
 def test_child_does_not_inherit_adult_art_or_progress(self):
  self.b.setBackgroundMode('fixed');self.b.setFixedBackground('drift');self.b.setProfile('child');self.assertEqual(self.b.backgroundArt,'')
  self.b.setBackgroundMode('dynamic');self.assertEqual([e['id'] for e in self.b.recentGames],['aurora']);self.b.focusItem('drift');self.assertNotEqual(self.b.featured.get('id'),'drift')
 def test_movie_background_and_demo_separation(self):
  self.b.navigate(2);self.b.focusItem('moon');self.assertEqual(self.b.backgroundArt,'moon');self.b.openDetail(1);self.assertNotIn('progress',self.b.detail)
  self.assertEqual(DemoProgressProvider().get('adult','missing'),{})
