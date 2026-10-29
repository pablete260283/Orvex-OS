"""State/gesture simulation plus a real, owned Win32 window in Windows CI."""

import sys
import time
import unittest
from unittest.mock import Mock

from PySide6.QtCore import QProcess
from PySide6.QtTest import QTest

import test_real_ui
from artifacts import capture_dir
from orvex.controls.gamepad import NavigationInput, xinput_actions
from orvex.controls.system_gesture import SystemGesture
from orvex.runtime.quick_menu import FocusPausePolicy
from orvex.runtime.window_control import WindowControl
from orvex.ui_runtime import ui_application
from real_fixture import build_fixture
from test_controller import Reader
from ui_selectors import find_item


class QuickMenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = ui_application()

    setUp = test_real_ui.RealUiTests.setUp
    tearDown = test_real_ui.RealUiTests.tearDown

    def start_session(self):
        self.exe = build_fixture(self.root, wait_for_release=True)
        self.b.importGame("Aplicación nativa controlada", "PC", str(self.exe))
        self.game_id = self.b.entries[0]["id"]
        self.b.requestLaunch(self.game_id)
        self.b.confirmLaunch()
        deadline = time.monotonic() + 3
        while not self.b.launcher.started and time.monotonic() < deadline:
            QTest.qWait(10)
        self.assertTrue(self.b.launchBusy)
        self.windows = Mock()
        self.windows.find.return_value = 123
        self.windows.focus.return_value = True
        self.windows.request_close.side_effect = (
            lambda *_: (self.exe.parent / "orvex-test-release.txt").touch() or True
        )
        self.b.quick_menu.windows = self.windows

    def overlay(self):
        for window in self.app.allWindows():
            if window.objectName() == "inGameOverlay":
                return window
        self.fail("Overlay missing")

    def action(self, action):
        self.reader.actions = set()
        self.router.poll()
        self.app.processEvents()
        self.reader.actions = {action}
        self.router.poll()
        self.app.processEvents()
        QTest.qWait(35)

    def test_popup_resume_controls_confirm_close_and_session_record(self):
        self.start_session()
        menu = self.b.quick_menu
        menu.open()
        QTest.qWait(80)
        overlay = self.overlay()
        self.assertTrue(overlay.isVisible())
        self.assertIn("no disponible", menu.message)
        self.reader = Reader()
        self.router = NavigationInput(
            target=lambda: self.overlay() if menu.state != "controls" else self.window
        )
        self.router.reader = self.reader
        self.router.poll()
        self.assertEqual(overlay.activeFocusItem().objectName(), "quickContinue")
        self.assertTrue(overlay.grabWindow().save(str(capture_dir("quick-menu") / "popup.png")))
        self.action("down")
        self.action("down")
        self.assertEqual(overlay.activeFocusItem().objectName(), "quickControls")
        self.action("confirm")
        self.assertEqual(menu.state, "controls")
        self.assertTrue(self.b.launchBusy)
        self.assertEqual(self.b.page, 3)
        self.action("back")
        self.assertEqual(menu.state, "menu")
        self.action("confirm")
        self.assertFalse(menu.opened)
        self.windows.focus.assert_called()
        self.assertTrue(self.b.launchBusy)
        menu.open()
        QTest.qWait(60)
        self.action("down")
        self.action("confirm")
        self.assertEqual(menu.state, "confirm-close")
        self.assertEqual(overlay.activeFocusItem().objectName(), "quickCancelClose")
        self.action("back")
        self.assertEqual(menu.state, "menu")
        self.windows.request_close.assert_not_called()
        menu.ask_close()
        menu.close_game()
        deadline = time.monotonic() + 3
        while self.b.launchBusy and time.monotonic() < deadline:
            QTest.qWait(20)
        self.assertFalse(self.b.launchBusy)
        self.assertEqual(menu.state, "closed")
        self.assertEqual(self.b.page, 1)
        self.assertEqual(
            self.store.db.execute("SELECT status FROM play_sessions").fetchone()[0], "finished"
        )
        self.router.timer.stop()

    def test_system_held_gesture_learning_disconnect_and_reserved_bits(self):
        self.start_session()
        gesture = SystemGesture(self.b)
        gesture.update(set(), 0)
        gesture.update({"guide"}, 1)
        gesture.update({"guide"}, 2)
        self.assertTrue(self.b.quick_menu.opened)
        gesture.update({"guide"}, 3)
        self.assertTrue(self.b.quick_menu.opened)  # no repeat
        gesture.update(set(), 4)
        gesture.update({"view", "menu"}, 5)
        gesture.update({"view", "menu"}, 6)
        self.assertFalse(self.b.quick_menu.opened)
        self.assertNotIn("guide", xinput_actions(0x0400))  # reserved != Guide
        gesture.update(set(), 7, reset=True)
        gesture.update({"guide"}, 8)
        gesture.update({"guide"}, 9)
        self.assertFalse(self.b.quick_menu.opened)
        self.b.beginShortcutCapture()
        gesture.update(set(), 10)
        gesture.update({"raw-9", "raw-10"}, 11)
        gesture.update({"raw-9", "raw-10"}, 12)
        self.assertEqual(self.store.get("quick_menu_buttons"), ["raw-10", "raw-9"])
        self.assertFalse(self.b.shortcut_capture)

    def test_close_failure_and_unexpected_exit_leave_no_stuck_menu(self):
        self.start_session()
        self.windows.request_close.side_effect = None
        self.windows.request_close.return_value = False
        menu = self.b.quick_menu
        menu.open()
        menu.ask_close()
        menu.close_game()
        self.assertEqual(menu.state, "menu")
        self.assertIn("No se pudo", menu.message)
        self.assertTrue(self.b.launchBusy)
        (self.exe.parent / "orvex-test-release.txt").touch()
        deadline = time.monotonic() + 3
        while self.b.launchBusy and time.monotonic() < deadline:
            QTest.qWait(20)
        self.assertFalse(menu.opened)

    def test_pause_config_is_read_only_conservative_and_engine_specific(self):
        path = self.root / "Dolphin.ini"
        path.write_text("[Interface]\nPauseOnFocusLost = True\n", encoding="utf-8")
        before = path.read_bytes()
        self.assertTrue(self.b.approvePauseConfig("dolphin", str(path)))
        self.assertTrue(FocusPausePolicy.configured(self.store, "dolphin"))
        self.assertFalse(FocusPausePolicy.configured(self.store, "pcsx2"))
        self.assertFalse(FocusPausePolicy.configured(self.store, "native"))
        self.assertEqual(before, path.read_bytes())
        path.write_text("[Interface]\nPauseOnFocusLost = nonsense\n", encoding="utf-8")
        self.assertFalse(FocusPausePolicy.configured(self.store, "dolphin"))

    def test_native_window_close_or_explicit_unsupported(self):
        service = WindowControl()
        if sys.platform != "win32":
            self.assertFalse(service.find(123))
            self.assertFalse(service.request_close(123, 123))
            return
        exe = build_fixture(self.root, gui=True)
        process = QProcess()
        process.setWorkingDirectory(str(exe.parent))
        process.start(str(exe), [])
        self.assertTrue(process.waitForStarted(3000))
        try:
            pid = process.processId()
            deadline = time.monotonic() + 4
            handle = 0
            while not handle and time.monotonic() < deadline:
                QTest.qWait(25)
                handle = service.find(pid)
            self.assertTrue(handle, process.readAllStandardError().data().decode(errors="replace"))
            self.assertFalse(service.request_close(handle, pid + 1))
            self.assertTrue(service.request_close(handle, pid))
            self.assertTrue(process.waitForFinished(3000))
            self.assertEqual(process.exitCode(), 0)
            self.assertTrue((exe.parent / "orvex-test-close-request.txt").exists())
        finally:
            if process.state() != QProcess.NotRunning:
                process.kill()  # test-owned fixture cleanup only, never product behavior
                process.waitForFinished(2000)

    def test_sdl_mapped_guide_disconnect_and_fallback_are_single_source(self):
        from orvex.controls.sdl_navigation import SDLNavigation

        lib = Mock()
        lib.SDL_NumJoysticks.return_value = 1
        lib.SDL_IsGameController.return_value = 1
        lib.SDL_GameControllerOpen.return_value = 321
        lib.SDL_GameControllerGetAttached.return_value = 1
        lib.SDL_GameControllerGetButton.side_effect = lambda handle, button: button == 5
        lib.SDL_GameControllerGetAxis.return_value = 0
        fallback = Mock()
        fallback.connection_token = 0
        fallback.read.return_value = {"confirm"}
        reader = SDLNavigation(Mock(library=lib), fallback)
        self.assertIn("guide", reader.read())
        fallback.read.assert_not_called()
        lib.SDL_GameControllerGetAttached.return_value = 0
        lib.SDL_NumJoysticks.return_value = 0
        self.assertEqual(reader.read(), {"confirm"})
        lib.SDL_GameControllerClose.assert_called_once_with(321)
        reader.close()

    def test_exit_from_controller_settings_closes_modal_and_restores_library(self):
        from PySide6.QtCore import QObject

        self.start_session()
        menu = self.b.quick_menu
        menu.open()
        QTest.qWait(30)
        overlay = self.overlay()
        self.reader = Reader()
        self.router = NavigationInput(
            target=lambda: overlay if menu.state != "controls" else self.window
        )
        self.router.reader = self.reader
        self.router.poll()
        self.action("down")
        self.action("down")
        self.action("confirm")
        find_item(self.window, "openControllerManager").forceActiveFocus()
        self.action("confirm")
        manager = self.window.findChild(QObject, "controllerManager")
        self.assertTrue(manager.property("opened"))
        (self.exe.parent / "orvex-test-release.txt").touch()
        deadline = time.monotonic() + 3
        while self.b.launchBusy and time.monotonic() < deadline:
            QTest.qWait(20)
        QTest.qWait(60)
        self.assertFalse(manager.property("opened"))
        self.assertEqual(self.b.page, 1)
        self.assertFalse(menu.opened)
        self.assertTrue(self.window.activeFocusItem().objectName().startswith("recent-"))
        self.router.timer.stop()
