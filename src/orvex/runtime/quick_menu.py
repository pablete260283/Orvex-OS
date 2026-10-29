"""Quick-menu state machine. Unsupported pause degrades explicitly; never toggles blindly."""

import configparser
from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot

from .window_control import WindowControl


class FocusPausePolicy:
    KEYS = {"dolphin": ("Interface", "PauseOnFocusLost"), "pcsx2": ("UI", "PauseOnFocusLoss")}

    @classmethod
    def configured(cls, store, engine):
        if engine not in cls.KEYS:
            return False
        path = store.get("quick_pause_config_" + engine, "")
        if not path:
            return False
        try:
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            parser.read_string(Path(path).read_text(encoding="utf-8-sig"))
            section, key = cls.KEYS[engine]
            return parser.getboolean(section, key, fallback=False)
        except (OSError, ValueError, configparser.Error):
            return False


class QuickMenu(QObject):
    changed = Signal()
    focus_game_requested = Signal()
    returned = Signal()

    def __init__(self, launcher, store, windows=None, parent=None):
        super().__init__(parent)
        self.launcher = launcher
        self.store = store
        self.windows = windows or WindowControl()
        self.mode = "closed"
        self.notice = ""
        self.handle = 0
        self.pid = 0
        self.engine = "native"
        launcher.changed.connect(self.session_changed)

    @Property(str, notify=changed)
    def state(self):
        return self.mode

    @Property(bool, notify=changed)
    def opened(self):
        return self.mode != "closed"

    @Property(str, notify=changed)
    def message(self):
        return self.notice

    def session_changed(self):
        if not self.launcher.busy and self.opened:
            self.mode = "closed"
            self.handle = self.pid = 0
            self.changed.emit()
            self.returned.emit()

    @Slot()
    def open(self):
        if not self.launcher.busy or self.opened:
            return
        self.pid = int(self.launcher.process.processId())
        if not self.pid:
            return
        self.handle = self.windows.find(self.pid)
        self.engine = "native"
        for engine in ("dolphin", "pcsx2"):
            if self.store.db.execute(
                f"SELECT 1 FROM {engine}_roms WHERE game_id=?", (self.launcher.game_id,)
            ).fetchone():
                self.engine = engine
                break
        configured = FocusPausePolicy.configured(self.store, self.engine)
        self.notice = (
            "Pausa al perder foco configurada en el emulador. Estado no observable; verifica que el juego se detenga."
            if configured and self.handle
            else "Pausa automática no disponible o no verificada. El juego puede seguir ejecutándose."
        )
        self.mode = "menu"
        self.changed.emit()

    @Slot()
    def controls(self):
        if self.mode == "menu":
            self.mode = "controls"
            self.changed.emit()

    @Slot()
    def back(self):
        if self.mode != "menu" and self.opened:
            self.mode = "menu"
            self.changed.emit()
        else:
            self.resume()

    @Slot()
    def resume(self):
        if not self.opened:
            return
        if self.launcher.busy and not self.windows.focus(self.handle, self.pid):
            self.notice = "Windows no permitió devolver el foco. Selecciona la ventana del juego."
        self.mode = "closed"
        self.changed.emit()
        self.focus_game_requested.emit()

    @Slot()
    def ask_close(self):
        if self.mode == "menu":
            self.mode = "confirm-close"
            self.changed.emit()

    @Slot()
    def close_game(self):
        if self.mode != "confirm-close" or not self.launcher.busy:
            return
        if not self.windows.request_close(self.handle, self.pid):
            self.notice = (
                "No se pudo solicitar un cierre seguro. Vuelve al juego y ciérralo desde su menú."
            )
            self.mode = "menu"
        else:
            self.notice = "Cierre solicitado. Guarda y confirma en el juego si lo pide. ORVEX no forzará su salida."
            self.mode = "waiting-close"
            self.windows.focus(self.handle, self.pid)
        self.changed.emit()
