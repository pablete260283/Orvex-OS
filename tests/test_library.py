import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from orvex.core.store import Store,catalog
from orvex.core.library import LibraryService
from orvex.core.bridge import Bridge

class LibraryTests(unittest.TestCase):
    def setUp(self):self.store=Store(':memory:');self.service=LibraryService(self.store);self.store.set("library_source","demo");self.b=Bridge(self.store)
    def tearDown(self):self.store.close()
    def test_search_and_platform_combined(self):
        self.assertEqual([e['id'] for e in self.service.query('adult','game',' ORBITA ','PC')],['orbit'])
        self.assertEqual(self.service.query('adult','game','orbita','Arcade'),[])
    def test_media_type_and_synopsis(self):
        entries=self.service.query('adult','media',category='Serie')
        self.assertEqual({e['id'] for e in entries},{'signal','cosmos'})
        self.assertTrue(all(e['description'] and isinstance(e['age'],int) and e['availability'] for e in entries))
    def test_child_filter_every_surface(self):
        for page in [0,1,2]:
            self.b.navigate(page);self.b.setProfile('child')
            self.assertTrue(all(e['age']<=7 for e in self.b.entries))
            self.assertFalse(any(e['id'] in {'orbit','drift','moon','signal'} for e in self.b.entries))
        self.b.navigate(2);self.b.setQuery('señal');self.assertEqual(self.b.entries,[])
        self.assertNotIn('Película',self.b.options)
    def test_unknown_age_fails_closed(self):
        s=LibraryService(self.store,[dict(id=str(i),title='x',kind='media',age=age) for i,age in enumerate([None,'7',False,-1,18,0,7])])
        self.assertEqual([e['age'] for e in s.visible('child')],[0,7])
        self.assertEqual(s.visible('invalid'),[])
    def test_favorites_profile_isolation(self):
        self.assertTrue(self.service.toggle_favorite('signal','adult'))
        self.assertEqual(self.service.query('child','media',favorites_only=True),[])
        self.assertFalse(self.service.toggle_favorite('signal','child'))
        self.assertTrue(self.service.toggle_favorite('aurora','child'))
        self.assertEqual([e['id'] for e in self.service.query('child',favorites_only=True)],['aurora'])
        self.service.toggle_favorite('aurora','child');self.assertEqual(self.store.favorites('child'),[])
    def test_detail_return_retains_state(self):
        self.b.navigate(1);self.b.setCategory('PC');self.b.setQuery('o');self.b.selectIndex(1)
        before=(self.b.query,self.b.category,self.b.selectedIndex)
        self.b.openDetail(1);self.assertEqual(self.b.detail['id'],'orbit');self.b.closeDetail()
        self.assertEqual((self.b.query,self.b.category,self.b.selectedIndex),before)
        self.b.navigate(2);self.b.navigate(1);self.assertEqual((self.b.query,self.b.category,self.b.selectedIndex),before)
    def test_profile_switch_closes_adult_detail_and_search(self):
        self.b.navigate(2);self.b.setQuery('luna');self.b.openDetail(0);self.assertTrue(self.b.detailOpen)
        self.b.setProfile('child');self.assertFalse(self.b.detailOpen);self.assertEqual(self.b.detail,{})
        self.assertEqual(self.b.query,'');self.assertTrue(all(e['age']<=7 for e in self.b.entries))
        self.b.setProfile('adult');self.assertEqual(self.b.query,'luna')
    def test_empty_results_and_filtered_favorite_removal(self):
        self.b.navigate(1);self.b.toggleFavorite('aurora');self.b.toggleFavorites();self.b.openDetail(0)
        self.b.toggleFavorite('aurora');self.assertEqual(self.b.entries,[]);self.assertTrue(self.b.detailOpen)
        self.b.closeDetail();self.assertEqual(self.b.selectedIndex,0)
        self.b.setQuery('nonexistent');self.assertEqual(self.b.entries,[])
    def test_migration_and_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'prefs.sqlite3';db=sqlite3.connect(path)
            db.execute('CREATE TABLE settings (key TEXT PRIMARY KEY,value TEXT NOT NULL)');db.execute('INSERT INTO settings VALUES (?,?)',('reduced_motion','true'));db.execute('PRAGMA user_version=1');db.commit();db.close()
            s=Store(path);b=Bridge(s);self.assertTrue(b.reducedMotion);b.setProfile('child');b.toggleFavorite('aurora');s.close()
            s=Store(path);b=Bridge(s);self.assertEqual(b.profile,'child');self.assertTrue(b.reducedMotion);self.assertEqual(s.favorites('child'),['aurora']);self.assertEqual(s.db.execute('PRAGMA user_version').fetchone()[0],5);s.close()
