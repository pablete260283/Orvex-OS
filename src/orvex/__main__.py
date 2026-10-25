import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths, QUrl
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from .core.store import Store
from .core.bridge import Bridge

def configure_application(app):
    app.setOrganizationName("ORVEX")
    # Retain the 0.1 preference location; expose the official application name.
    app.setApplicationName("Entertainment Preview")
    path = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    app.setApplicationName("ORVEX OS")
    app.setApplicationDisplayName("ORVEX OS")
    icon = QIcon(str(Path(__file__).parent / "ui/assets/brand/svg/orvex-app-icon-dark.svg"))
    if icon.isNull():
        icon = QIcon(str(Path(__file__).parent / "ui/assets/brand/png/orvex-app-icon-dark-4x.png"))
    app.setWindowIcon(icon)
    return path

def main():
    app = QGuiApplication(sys.argv)
    path = configure_application(app)
    path.mkdir(parents=True, exist_ok=True)
    store = Store(path / "preferences.sqlite3")
    bridge = Bridge(store)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", bridge)
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / "ui/Main.qml")))
    if not engine.rootObjects():
        store.close()
        return 1
    result = app.exec()
    del engine
    store.close()
    return result

if __name__ == "__main__":
    raise SystemExit(main())
