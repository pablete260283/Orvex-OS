import base64
import json
import hashlib
import unittest
from html.parser import HTMLParser
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtSvg import QSvgRenderer
from orvex.__main__ import configure_application

ROOT=Path(__file__).parents[1]
BRAND=ROOT/"src/orvex/ui/assets/brand"
class Tags(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.tags=[]; self.feed(text)
    def handle_starttag(self,tag,attrs):
        self.tags.append((tag,dict(attrs)))

class BrandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QGuiApplication.instance() or QGuiApplication([])
    def test_svg_resources_are_valid(self):
        for p in (BRAND/"svg").glob("*.svg"):
            self.assertTrue(QSvgRenderer(str(p)).isValid(),p.name)
        for name,digest in json.loads((BRAND/"SHA256.json").read_text()).items():
            self.assertEqual(hashlib.sha256((BRAND/name).read_bytes()).hexdigest(),digest,name)
    def test_html_uses_original_svg_and_png(self):
        for version in ["0.1","0.2"]:
            text=(ROOT/("preview/ORVEX-"+version+".html")).read_text()
            tags=Tags(text).tags
            logo=next(a for tag,a in tags if tag=="img" and a.get("class")=="logo")
            self.assertEqual(logo["alt"],"ORVEX OS")
            self.assertEqual(base64.b64decode(logo["src"].split(",")[1]),(BRAND/"svg/orvex-horizontal-dark.svg").read_bytes())
            fallback=logo["onerror"].split("data:image/png;base64,")[1].split("'")[0]
            self.assertEqual(base64.b64decode(fallback),(BRAND/"png/orvex-horizontal-dark-4x.png").read_bytes())
            favicon=next(a for tag,a in tags if tag=="link" and a.get("rel")=="icon")
            self.assertEqual(base64.b64decode(favicon["href"].split(",")[1]),(BRAND/"svg/orvex-app-icon-dark.svg").read_bytes())
            self.assertIn("<title>ORVEX OS "+version,text)
    def test_app_name_icon_and_preference_location(self):
        path=configure_application(self.app)
        self.assertEqual(self.app.applicationName(),"ORVEX OS")
        self.assertEqual(self.app.applicationDisplayName(),"ORVEX OS")
        self.assertEqual(path.name,"Entertainment Preview")
        self.assertFalse(self.app.windowIcon().pixmap(256,256).isNull())
