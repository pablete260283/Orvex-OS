"""Semantic controller events through the production input router, without hardware."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
import unittest
import shutil
import tempfile
from pathlib import Path
from PySide6.QtCore import QMetaObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest
from orvex.controls.gamepad import NavigationInput, xinput_actions, winmm_actions, Joy, State
from orvex.core.bridge import Bridge
from orvex.core.store import Store
from real_fixture import build_fixture
import test_ui
from ui_selectors import find_item
from artifacts import capture_dir


class Reader:
    def __init__(self):
        self.actions = set()

    def read(self):
        return self.actions


class InputTests(unittest.TestCase):
    def test_native_mappings_and_deadzone(self):
        import ctypes

        self.assertEqual(ctypes.sizeof(Joy), 52)
        self.assertEqual(ctypes.sizeof(State), 16)
        self.assertEqual(xinput_actions(0x1001, 2000, 1000), {"confirm", "up"})
        self.assertEqual(xinput_actions(0, 20000, -20000), {"right", "down"})
        self.assertEqual(winmm_actions(2, 9000), {"confirm", "right"})
        self.assertEqual(winmm_actions(4), {"back"})
        self.assertEqual(winmm_actions(0), set())

    def test_confirm_not_repeated_direction_repeat_and_resume_gate(self):
        reader = Reader()
        events = []
        enabled = [True]
        router = NavigationInput(reader=None, target=lambda: True, enabled=lambda: enabled[0])
        router.reader = reader
        router.dispatch = events.append
        router.poll(0)
        reader.actions = {"confirm"}
        router.poll(0.1)
        router.poll(1)
        self.assertEqual(events, ["confirm"])
        reader.actions = set()
        router.poll(2)
        reader.actions = {"right"}
        router.poll(3)
        router.poll(3.1)
        router.poll(3.5)
        self.assertEqual(events, ["confirm", "right", "right"])
        enabled[0] = False
        router.poll(4)
        enabled[0] = True
        reader.actions = {"confirm"}
        router.poll(5)
        self.assertEqual(events[-1], "right")
        reader.actions = set()
        router.poll(6)
        reader.actions = {"confirm", "back"}
        router.poll(7)
        self.assertEqual(events[-1], "back")

    def test_linux_event_decoder_and_nonblocking_reader(self):
        import struct
        from unittest.mock import patch
        from orvex.controls.linux_joystick import LinuxJoystick

        reader = LinuxJoystick()
        reader.fd = 123
        data = [struct.pack("=IhBB", 0, 1, 0x81, 0), struct.pack("=IhBB", 1, 32767, 2, 6)]
        with patch("orvex.controls.linux_joystick.os.read", side_effect=data + [BlockingIOError()]):
            self.assertEqual(reader.read(), {"confirm", "right"})
        reader.fd = None

    def test_remote_select_back_and_repeat_suppression(self):
        from PySide6.QtCore import QEvent, Qt
        from PySide6.QtGui import QKeyEvent

        router = NavigationInput(target=lambda: True)
        events = []
        router.dispatch = events.append
        self.assertTrue(
            router.eventFilter(None, QKeyEvent(QEvent.KeyPress, Qt.Key_Select, Qt.NoModifier))
        )
        router.eventFilter(None, QKeyEvent(QEvent.KeyPress, Qt.Key_Select, Qt.NoModifier, "", True))
        router.eventFilter(None, QKeyEvent(QEvent.KeyRelease, Qt.Key_Select, Qt.NoModifier))
        router.eventFilter(None, QKeyEvent(QEvent.KeyPress, Qt.Key_Back, Qt.NoModifier))
        self.assertEqual(events, ["confirm", "back"])

    def test_full_catalog_recent_order_and_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            exe = build_fixture(root)
            store = Store(root / "prefs.db")
            b = Bridge(store)
            ids = []
            for n in range(15):
                target = root / ("game" + str(n) + exe.suffix)
                shutil.copy2(exe, target)
                ids.append(b.installed.import_game("Game " + str(n).zfill(2), "PC", str(target)))
            for key, date in [
                (ids[3], "2026-10-25T12:00:00+00:00"),
                (ids[8], "2026-10-26T12:00:00+00:00"),
            ]:
                store.db.execute(
                    "INSERT INTO play_sessions(game_id,started_at,status,duration_ms) VALUES(?,?,?,?)",
                    (key, date, "finished", 321),
                )
            store.db.commit()
            b.refresh()
            self.assertEqual(len(b.showcase), 15)
            self.assertEqual([e["id"] for e in b.showcase[:2]], [ids[8], ids[3]])
            self.assertEqual(b.showcase[2]["title"], "Game 00")
            b.romTimer.stop()
            store.close()
            store = Store(root / "prefs.db")
            b = Bridge(store)
            self.assertEqual(b.showcase[0]["id"], ids[8])
            self.assertEqual(
                store.db.execute("SELECT SUM(duration_ms) FROM play_sessions").fetchone()[0], 642
            )
            b.romTimer.stop()
            store.close()


class ControllerUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    setUp = test_ui.UiTests.setUp
    tearDown = test_ui.UiTests.tearDown

    def action(self, value):
        self.reader.actions = set()
        self.router.poll()
        self.app.processEvents()
        self.reader.actions = {value}
        self.router.poll()
        self.app.processEvents()
        QTest.qWait(35)

    def choose(self, index):
        keys = find_item(self.window, "virtualKeyboard")
        while keys.property("currentIndex") != index:
            self.action("right")
        self.action("confirm")

    def test_search_confirm_cancel_return_and_section_scope(self):
        self.reader = Reader()
        self.router = NavigationInput(target=lambda: self.window)
        self.router.reader = self.reader
        self.router.poll()
        self.action("up")
        self.assertEqual(self.window.activeFocusItem().objectName(), "searchButton")
        self.action("confirm")
        keys = find_item(self.window, "virtualKeyboard")
        self.assertTrue(keys.hasActiveFocus())
        self.action("confirm")
        self.assertEqual(self.b.query, "a")
        self.assertTrue(keys.hasActiveFocus())
        self.choose(26)
        self.assertEqual(self.b.query, "añ")
        self.choose(47)
        self.assertEqual(self.b.query, "a")
        self.choose(46)
        self.assertEqual(self.b.query, "a ")
        self.choose(48)
        self.assertEqual(self.b.query, "")
        self.choose(0)
        self.choose(49)
        self.assertTrue(self.window.activeFocusItem().objectName().startswith("recent-"))
        self.action("confirm")
        self.assertTrue(self.b.detailOpen)
        self.assertEqual(self.window.activeFocusItem().objectName(), "demoPlay")
        self.action("back")
        self.assertFalse(self.b.detailOpen)
        self.assertTrue(self.window.activeFocusItem().objectName().startswith("recent-"))
        self.action("up")
        self.action("confirm")
        self.choose(25)
        self.assertEqual(self.b.query, "az")
        self.action("back")
        self.assertEqual(self.b.query, "a")
        self.b.navigate(2)
        self.b.setQuery("océano")
        self.assertTrue(all(e["kind"] != "game" for e in self.b.showcase))
        self.b.setQuery("this cannot match")
        QMetaObject.invokeMethod(find_item(self.window, "consolePage"), "restore")
        QTest.qWait(50)
        self.assertEqual(self.b.showcase, [])
        self.assertEqual(self.window.activeFocusItem().objectName(), "searchButton")
        self.action("confirm")
        self.choose(48)
        self.assertEqual(self.b.query, "")
        self.window.resize(1920, 1080)
        QTest.qWait(50)
        out = capture_dir("minimal")
        self.window.grabWindow().save(str(out / "search-1080.png"))
        self.choose(49)
        self.window.grabWindow().save(str(out / "main-1080.png"))
        self.action("up")
        self.action("right")
        self.assertEqual(self.window.activeFocusItem().objectName(), "profileButton")
        self.action("confirm")
        self.action("down")
        self.action("confirm")
        self.assertEqual(self.b.profile, "child")
        self.action("up")
        self.action("right")
        self.action("confirm")
        self.action("confirm")
        self.assertEqual(self.b.profile, "adult")
        self.action("up")
        self.action("right")
        self.action("right")
        self.action("confirm")
        self.assertEqual(self.b.page, 3)
        self.action("back")
        self.assertEqual(self.b.page, 1)
        self.router.timer.stop()


class ControllerLaunchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    import test_real_ui as _real

    setUp = _real.RealUiTests.setUp
    tearDown = _real.RealUiTests.tearDown
    action = ControllerUiTests.action

    def test_real_process_confirm_and_return_using_router(self):
        self.reader = Reader()
        self.router = NavigationInput(
            target=lambda: self.window, enabled=lambda: not self.b.launchBusy
        )
        self.router.reader = self.reader
        self.router.poll()
        self.b.importGame("Proceso controlado", "PC Linux", str(self.exe))
        QTest.qWait(100)
        QMetaObject.invokeMethod(find_item(self.window, "consolePage"), "restore")
        QTest.qWait(30)
        self.action("confirm")
        self.assertTrue(self.b.detailOpen)
        self.action("confirm")
        self.assertTrue(self.b.pendingLaunch)
        self.assertFalse(self.b.launchBusy)
        self.assertEqual(self.window.activeFocusItem().objectName(), "cancelLaunch")
        self.action("left")
        self.assertEqual(self.window.activeFocusItem().objectName(), "confirmLaunch")
        self.action("confirm")
        self.router.poll()
        QTest.qWait(400)
        self.app.processEvents()
        self.assertFalse(self.b.launchBusy)
        self.assertFalse(self.b.pendingLaunch)
        self.assertEqual(
            self.store.db.execute("SELECT COUNT(*) FROM play_sessions").fetchone()[0], 1
        )
        self.assertGreater(
            self.store.db.execute("SELECT duration_ms FROM play_sessions").fetchone()[0], 0
        )
        self.action("back")
        self.assertFalse(self.b.detailOpen)
        self.router.timer.stop()
