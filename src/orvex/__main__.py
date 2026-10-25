import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from .core.store import Store
from .core.bridge import Bridge

def main():
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("ORVEX")
    app.setApplicationName("Entertainment Preview")
    path = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
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
