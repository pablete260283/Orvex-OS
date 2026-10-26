import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths, QUrl, QLockFile
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from .core.store import Store, StoreOpenError
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

    def storage_failure(error):
        engine = QQmlApplicationEngine()
        engine.rootContext().setContextProperty("storageError", str(error))
        engine.rootContext().setContextProperty("storagePath", str(path / "preferences.sqlite3"))
        engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / "ui/StorageError.qml")))
        if engine.rootObjects():
            app.exec()
        return 1

    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        return storage_failure(error)
    lock = QLockFile(str(path / "orvex.lock"))
    if not lock.tryLock(0):
        print("ORVEX ya está ejecutándose para este usuario.")
        return 1
    try:
        store = Store(path / "preferences.sqlite3")
        store.recover_sessions()
    except (StoreOpenError, OSError) as error:
        return storage_failure(error)
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
