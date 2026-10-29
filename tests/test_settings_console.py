"""Production Qt controls and semantic pad router. No physical controller claims."""

import unittest

from PySide6.QtCore import QObject, QMetaObject
from PySide6.QtTest import QTest

import test_real_ui
from artifacts import capture_dir
from orvex.controls.gamepad import NavigationInput
from orvex.core.bridge import Bridge
from orvex.core.store import Store
from orvex.ui_runtime import ui_application
from test_controller import Reader
from ui_selectors import find_item


class SettingsConsoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = ui_application()

    setUp = test_real_ui.RealUiTests.setUp
    tearDown = test_real_ui.RealUiTests.tearDown

    def action(self, action):
        self.reader.actions = set()
        self.router.poll()
        self.app.processEvents()
        self.reader.actions = {action}
        self.router.poll()
        self.app.processEvents()
        QTest.qWait(30)

    def start(self):
        self.reader = Reader()
        self.router = NavigationInput(target=lambda: self.window)
        self.router.reader = self.reader
        self.router.poll()
        self.b.navigate(3)
        QTest.qWait(60)

    def category(self, n):
        self.b.navigate(3)
        QTest.qWait(80)
        item = find_item(self.window, "settingsCategory-" + str(n))
        item.forceActiveFocus()
        self.action("confirm")
        self.assertEqual(self.window.findChild(QObject, "settingsPage").property("category"), n)

    def snap(self, name):
        QTest.qWait(60)
        self.assertTrue(
            self.window.grabWindow().save(str(capture_dir("settings") / (name + ".png")))
        )

    def test_six_sections_focus_actions_and_saved_preferences(self):
        self.start()
        self.assertEqual(self.window.activeFocusItem().objectName(), "settingsCategory-0")
        for n in range(6):
            self.category(n)
            self.assertTrue(self.window.activeFocusItem().isVisible())
            self.assertTrue(self.window.activeFocusItem().isEnabled())
            self.window.resize(1920, 1080)
            self.snap("section-" + str(n))
            for _ in range(5):
                self.action("down")
                self.assertTrue(self.window.activeFocusItem().isVisible())
                item = self.window.activeFocusItem()
                from PySide6.QtCore import QPointF

                point = item.mapToScene(QPointF(0, 0))
                self.assertGreaterEqual(point.y(), -1)
                self.assertLessEqual(
                    point.y() + item.height() * self.window.width() / 1920, self.window.height() + 2
                )
            self.action("back")
            if self.b.page != 3:
                self.b.navigate(3)
        self.category(0)
        motion = self.b.reducedMotion
        find_item(self.window, "reducedMotion").forceActiveFocus()
        self.action("confirm")
        self.assertEqual(self.b.reducedMotion, not motion)
        self.category(1)
        layout = self.b.controllerLayout
        find_item(self.window, "controllerLayout").forceActiveFocus()
        self.action("confirm")
        self.assertNotEqual(self.b.controllerLayout, layout)
        reopened = Store(self.root / "test.sqlite3")
        other = Bridge(reopened)
        self.assertEqual(other.reducedMotion, self.b.reducedMotion)
        self.assertEqual(other.controllerLayout, self.b.controllerLayout)
        other.romTimer.stop()
        reopened.close()
        self.router.timer.stop()

    def test_many_long_names_combo_text_selection_and_empty_state(self):
        self.start()
        self.category(3)
        self.snap("empty-library")
        combo = find_item(self.window, "managedGames")
        self.assertFalse(combo.isEnabled())
        for n in range(60):
            self.store.db.execute(
                "INSERT INTO real_games(id,name,platform,executable,arguments,created_at) VALUES(?,?,?,?,?,?)",
                (
                    "local-ui-" + str(n),
                    f"{n:02d} · Just Dance 2020 (USA) (En,Fr,Es) · nombre largo de prueba",
                    "Wii",
                    str(self.exe) + "::" + str(n),
                    "[]",
                    "2026-10-29",
                ),
            )
        self.store.db.commit()
        self.b.refresh()
        QTest.qWait(80)
        self.assertEqual(combo.property("count"), 60)
        self.assertTrue(self.window.findChild(QObject, "editGameName").property("text"))
        for size in ((1920, 1080), (1280, 720), (960, 540)):
            self.window.resize(*size)
            combo.forceActiveFocus()
            self.snap("library-closed-" + str(size[0]))
            self.action("confirm")
            popup = self.window.findChild(QObject, "managedGames-popup")
            self.assertTrue(popup.property("opened"))
            self.assertLessEqual(popup.property("height"), 328)
            option = find_item(self.window, "comboOption-0")
            self.assertIn("Just Dance", option.property("text"))
            # Check the rendered Text content, not only the model or delegate.text.
            texts = [x.property("text") for x in option.findChildren(QObject)]
            self.assertTrue(any(isinstance(t, str) and "Just Dance" in t for t in texts))
            self.snap("library-open-" + str(size[0]))
            self.action("down")
            self.action("confirm")
            self.assertFalse(popup.property("opened"))
            self.assertTrue(combo.hasActiveFocus())
            self.assertEqual(
                self.window.findChild(QObject, "editGameName").property("text"),
                combo.property("currentText"),
            )
        self.router.timer.stop()

    def test_controller_text_keyboard_save_cancel_and_edit_persistence(self):
        self.b.importGame("Nombre original", "PC", str(self.exe))
        self.start()
        self.category(3)
        field = find_item(self.window, "editGameName")
        field.forceActiveFocus()
        self.action("confirm")
        keys = find_item(self.window, "textEntryKeyboard")
        self.assertTrue(keys.hasActiveFocus())
        self.snap("text-keyboard")
        self.action("confirm")  # append a to draft only
        self.action("back")
        self.assertEqual(field.property("text"), "Nombre original")
        self.action("confirm")
        self.action("confirm")
        keys.setProperty("currentIndex", 62)  # Guardar
        self.action("confirm")
        self.assertEqual(field.property("text"), "Nombre originala")
        find_item(self.window, "saveGameEdits").forceActiveFocus()
        self.action("confirm")
        reopened = Store(self.root / "test.sqlite3")
        self.assertEqual(
            reopened.db.execute("SELECT name FROM real_games").fetchone()[0], "Nombre originala"
        )
        reopened.close()
        self.router.timer.stop()

    def test_controller_file_browser_and_nested_dialog_return(self):
        from PySide6.QtCore import Q_ARG

        self.start()
        self.category(3)
        find_item(self.window, "emulatorSettings").forceActiveFocus()
        self.action("confirm")
        dialog = self.window.findChild(QObject, "emulatorDialog")
        self.assertTrue(dialog.property("opened"))
        self.snap("emulator-dialog")
        self.action("back")
        self.assertFalse(dialog.property("opened"))
        self.assertEqual(self.b.page, 3)
        # Open the same in-app browser used by import/artwork/profile pickers.
        browser = self.window.findChild(QObject, "fileBrowser")
        self.assertTrue(
            QMetaObject.invokeMethod(browser, "visit", Q_ARG("QVariant", str(self.root)))
        )
        self.assertTrue(QMetaObject.invokeMethod(browser, "open"))
        QTest.qWait(50)
        files = find_item(self.window, "browserFiles")
        files.forceActiveFocus()
        self.assertGreater(files.property("count"), 0)
        self.snap("file-browser")
        self.action("down")
        self.action("right")
        self.assertEqual(self.window.activeFocusItem().objectName(), "browserCancel")
        self.action("confirm")
        self.assertFalse(browser.property("opened"))
        result = self.b.browseDirectory(str(self.root / "missing"))
        self.assertTrue(result["error"])
        self.assertEqual(result["items"], [])
        self.router.timer.stop()

    def test_history_choice_can_be_toggled_and_cancelled_with_controller(self):
        self.b.importGame("Juego de prueba", "PC", str(self.exe))
        self.start()
        self.category(3)
        find_item(self.window, "removeGame").forceActiveFocus()
        self.action("confirm")
        dialog = self.window.findChild(QObject, "removalDialog")
        self.assertTrue(dialog.property("opened"))
        self.action("up")
        self.action("up")
        checkbox = self.window.activeFocusItem()
        self.assertEqual(checkbox.property("text"), "Conservar historial de sesiones")
        self.assertTrue(checkbox.property("checked"))
        self.action("confirm")
        self.assertFalse(checkbox.property("checked"))
        self.action("back")
        self.assertFalse(dialog.property("opened"))
        self.assertEqual(len(self.b.managedGames), 1)
        self.assertTrue(self.exe.is_file())
        find_item(self.window, "removeGame").forceActiveFocus()
        self.action("confirm")
        self.assertTrue(checkbox.property("checked"))
        self.action("confirm")  # safe default focus: Cancelar
        self.assertFalse(dialog.property("opened"))
        self.assertEqual(len(self.b.managedGames), 1)
        self.router.timer.stop()
