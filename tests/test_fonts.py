"""A rendered UI must contain actual Latin/Spanish glyphs, not only rectangles."""
import unittest
from PySide6.QtGui import QFontMetrics
from orvex.ui_runtime import ui_application

class FontTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = ui_application()

    def test_application_font_has_spanish_console_text(self):
        metrics = QFontMetrics(self.app.font())
        for character in 'ORVEX Videojuegos Configuración áéíóúñ 0123456789':
            with self.subTest(character=character):
                self.assertTrue(metrics.inFontUcs4(ord(character)))
