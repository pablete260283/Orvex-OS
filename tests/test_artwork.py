import json,tempfile,unittest
from pathlib import Path
from orvex.core.artwork import resolve_art,MANIFEST
from orvex.core.store import catalog,Store
from orvex.core.bridge import Bridge
class ArtworkTests(unittest.TestCase):
 def test_manifest_assets_and_demo_separation(self):
  for key in json.loads(MANIFEST.read_text()):
   for role in ['cover','backdrop']:self.assertTrue(resolve_art(key,role).startswith('file:'))
  self.assertTrue(all(e['catalog_source']=='demo' and e['installed'] is False for e in catalog()))
 def test_unapproved_missing_remote_and_escape_rejected(self):
  record={'cover':'../demo.json','source':'test','rights':'test','redistribution':True}
  self.assertEqual(resolve_art('x',manifest={'x':record}), '')
  for change in [{'redistribution':False},{'source':''},{'cover':'https://example.com/a.png'},{'cover':'missing.png'}]:
   self.assertEqual(resolve_art('x',manifest={'x':dict(record,**change)}),'')
 def test_start_route_showcase_independent_of_search_and_safe_profile(self):
  store=Store(':memory:');store.set('library_source','demo');b=Bridge(store);self.assertEqual(b.page,1)
  b.setQuery('nothing');self.assertEqual(b.entries,[]);self.assertEqual(len(b.showcase),3)
  b.openTitle('orbit');self.assertEqual(b.detail['id'],'orbit');b.closeDetail();self.assertEqual(b.query,'nothing')
  b.setProfile('child');b.openTitle('drift');self.assertFalse(b.detailOpen);self.assertEqual([e['id'] for e in b.showcase],['aurora']);store.close()
