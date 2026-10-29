"""Windows native polling, semantic navigation, and Qt event delivery.

No drivers or global hooks. XInput first; WinMM fallback for exposed HID pads.
Hardware-specific mappings still require physical validation.
"""

import ctypes as c
import sys
import time
from PySide6.QtCore import QObject, QTimer, QCoreApplication, QEvent, Qt, Signal
from PySide6.QtGui import QGuiApplication, QKeyEvent

KEYS = {
    "left": Qt.Key_Left,
    "right": Qt.Key_Right,
    "up": Qt.Key_Up,
    "down": Qt.Key_Down,
    "confirm": Qt.Key_Return,
    "back": Qt.Key_Escape,
}


class Pad(c.Structure):
    _fields_ = [
        ("buttons", c.c_uint16),
        ("lt", c.c_uint8),
        ("rt", c.c_uint8),
        ("lx", c.c_int16),
        ("ly", c.c_int16),
        ("rx", c.c_int16),
        ("ry", c.c_int16),
    ]


class State(c.Structure):
    _fields_ = [("packet", c.c_uint32), ("pad", Pad)]


class Joy(c.Structure):
    _fields_ = [
        (name, c.c_uint32)
        for name in [
            "size",
            "flags",
            "x",
            "y",
            "z",
            "r",
            "u",
            "v",
            "buttons",
            "number",
            "pov",
            "reserved1",
            "reserved2",
        ]
    ]


def xinput_actions(buttons, x=0, y=0):
    actions = set()
    for mask, action in [
        (1, "up"),
        (2, "down"),
        (4, "left"),
        (8, "right"),
        (0x1000, "confirm"),
        (0x2000, "back"),
    ]:
        if buttons & mask:
            actions.add(action)
    if abs(x) > 16000:
        actions.add("right" if x > 0 else "left")
    if abs(y) > 16000:
        actions.add("up" if y > 0 else "down")
    return actions


def winmm_actions(buttons, pov=65535, x=32767, y=32767, sony=True):
    actions = set()
    # Typical native Sony HID ordering: Square, Cross, Circle, Triangle.
    if buttons & (2 if sony else 1):
        actions.add("confirm")
    if buttons & (4 if sony else 2):
        actions.add("back")
    if pov in (0, 4500, 31500):
        actions.add("up")
    if pov in (9000, 4500, 13500):
        actions.add("right")
    if pov in (18000, 13500, 22500):
        actions.add("down")
    if pov in (27000, 22500, 31500):
        actions.add("left")
    if abs(x - 32767) > 16000:
        actions.add("right" if x > 32767 else "left")
    if abs(y - 32767) > 16000:
        actions.add("down" if y > 32767 else "up")
    return actions


class WindowsPad:
    def __init__(self, sony=True):
        self.xinput = None
        self.connection_token = 0
        self._source = None
        self.sony = sony
        for name in ("xinput1_4", "xinput1_3", "xinput9_1_0"):
            try:
                self.xinput = c.WinDLL(name).XInputGetState
                self.xinput.argtypes = [c.c_uint32, c.POINTER(State)]
                self.xinput.restype = c.c_uint32
                break
            except OSError:
                pass
        self.winmm = c.WinDLL("winmm").joyGetPosEx
        self.winmm.argtypes = [c.c_uint, c.POINTER(Joy)]
        self.winmm.restype = c.c_uint32

    def _connection(self, source):
        # A runtime source is only a navigation reset token, not a physical ID.
        if source != self._source:
            self._source = source
            self.connection_token += 1

    def read(self):
        if self.xinput:
            for index in range(4):
                state = State()
                if self.xinput(index, c.byref(state)) == 0:
                    p = state.pad
                    self._connection(("xinput", index))
                    return xinput_actions(p.buttons, p.lx, p.ly)
        for index in range(16):
            joy = Joy()
            joy.size = c.sizeof(Joy)
            joy.flags = 0xFF
            if self.winmm(index, c.byref(joy)) == 0:
                self._connection(("winmm", index))
                return winmm_actions(joy.buttons, joy.pov, joy.x, joy.y, self.sony)
        self._connection(None)
        return set()


class NavigationInput(QObject):
    """Edge-trigger confirm/back; direction-only repeat; neutral gate on return."""

    input_error_changed = Signal(str)

    def __init__(self, reader=None, target=None, enabled=None, parent=None):
        super().__init__(parent)
        self.reader = reader
        self.target = target or QGuiApplication.focusWindow
        self.enabled = enabled or (lambda: True)
        self.previous = set()
        self.last_connection = object()
        self.last_error = ""
        self.next_repeat = {}
        self.armed = False
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.poll)
        if reader:
            self.timer.start()

    def eventFilter(self, watched, event):
        if event.type() in (QEvent.KeyPress, QEvent.KeyRelease) and event.key() in (
            Qt.Key_Select,
            Qt.Key_Back,
        ):
            if event.type() == QEvent.KeyPress and not event.isAutoRepeat() and self.enabled():
                self.dispatch("confirm" if event.key() == Qt.Key_Select else "back")
            return True
        return False

    def dispatch(self, action):
        window = self.target()
        if not window or action not in KEYS:
            return
        for kind in (QEvent.KeyPress, QEvent.KeyRelease):
            QCoreApplication.postEvent(window, QKeyEvent(kind, KEYS[action], Qt.NoModifier))

    def poll(self, now=None):
        now = time.monotonic() if now is None else now
        try:
            actions = set(self.reader.read()) if self.reader else set()
            if self.last_error:
                self.last_error = ""
                self.input_error_changed.emit("")
        except (OSError, RuntimeError) as error:
            message = str(error)
            if self.last_error != message:
                self.last_error = message
                self.input_error_changed.emit(message)
            self.armed = False
            self.previous = set()
            self.next_repeat.clear()
            return
        connection = getattr(self.reader, "connection_token", None)
        if connection != self.last_connection:
            self.last_connection = connection
            self.armed = False
            self.previous = set()
            self.next_repeat.clear()
        if not self.enabled() or not self.target():
            self.armed = False
            self.previous = actions
            return
        if not self.armed:
            if not actions:
                self.armed = True
            self.previous = actions
            return
        # Never confirm and cancel on the same frame; back wins.
        if "back" in actions:
            actions.discard("confirm")
        for action in sorted(actions):
            fresh = action not in self.previous
            repeat = action in ("up", "down", "left", "right") and now >= self.next_repeat.get(
                action, now + 1
            )
            if fresh or repeat:
                self.dispatch(action)
                self.next_repeat[action] = now + (0.40 if fresh else 0.14)
        self.previous = actions


def create_navigation(bridge, parent):
    reader = (
        WindowsPad(bridge.store.get("controller_layout", "sony") == "sony")
        if sys.platform == "win32"
        else None
    )
    if sys.platform.startswith("linux"):
        from .linux_joystick import LinuxJoystick

        reader = LinuxJoystick()
        QGuiApplication.instance().aboutToQuit.connect(reader.close)
    navigation = NavigationInput(
        reader=reader, enabled=lambda: not bridge.launchBusy, parent=parent
    )
    navigation.input_error_changed.connect(bridge.reportControllerInputError)
    QGuiApplication.instance().installEventFilter(navigation)
    if sys.platform == "win32":
        bridge.operationChanged.connect(
            lambda: setattr(reader, "sony", bridge.controllerLayout == "sony")
        )
    return navigation
