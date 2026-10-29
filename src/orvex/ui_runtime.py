"""Initialize app fonts before QML/SVG rendering, including Windows offscreen QA."""

import os
import sys
from pathlib import Path
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication


def ensure_application_font(app):
    if app.property("orvexFontInitialized"):
        return
    if sys.platform == "win32":
        folder = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
        families = []
        # Register existing OS fonts for QPA offscreen; do not install/redistribute fonts.
        for name in ("segoeui.ttf", "segoeuib.ttf", "seguisym.ttf", "arial.ttf", "arialbd.ttf"):
            path = folder / name
            if path.is_file():
                identifier = QFontDatabase.addApplicationFont(str(path))
                if identifier >= 0:
                    families.extend(QFontDatabase.applicationFontFamilies(identifier))
        if families:
            app.setFont(QFont(families[0]))
    app.setProperty("orvexFontInitialized", True)


def ui_application():
    app = QGuiApplication.instance() or QGuiApplication([])
    ensure_application_font(app)
    return app
