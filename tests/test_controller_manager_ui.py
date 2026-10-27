import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
import unittest
from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest
import test_real_ui
from artifacts import capture_dir


class ManagerUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    setUp = test_real_ui.RealUiTests.setUp
    tearDown = test_real_ui.RealUiTests.tearDown
    click = test_real_ui.RealUiTests.click

    def test_manager_focus_and_capture(self):
        class FakeInventory:
            error = ""

            def devices(self):
                return [
                    dict(
                        name="Joy-Con (R) · PRUEBA",
                        family="joycon-r",
                        device_id="unit-id",
                        stable=True,
                        connection="simulada",
                        sensors="no verificado",
                    )
                ]

        self.b.controller_inventory = FakeInventory()
        self.b.controllers.inventory = self.b.controller_inventory
        self.b.navigate(3)
        QTest.qWait(60)
        self.click("settingsCategory-1")
        self.click("openControllerManager")
        QTest.qWait(80)
        self.assertEqual(self.window.activeFocusItem().objectName(), "controllerDevices")
        QTest.keyClick(self.window, Qt.Key_Down)
        QTest.qWait(20)
        self.assertEqual(self.window.activeFocusItem().property("text"), "Detectar mandos")
        QTest.keyClick(self.window, Qt.Key_Down)
        QTest.qWait(20)
        engine = self.window.activeFocusItem()
        self.assertEqual(engine.property("currentText"), "Dolphin")
        QTest.keyClick(self.window, Qt.Key_Right)
        QTest.qWait(40)
        self.assertEqual(engine.property("currentText"), "PCSX2")
        self.window.resize(1920, 1080)
        QTest.qWait(60)
        out = capture_dir("controller-manager")
        self.assertTrue(self.window.grabWindow().save(str(out / "manager-1080.png")))
        for _ in range(8):
            QTest.keyClick(self.window, Qt.Key_Down)
            QTest.qWait(10)
        self.assertIn("Aplicación temporal", self.window.activeFocusItem().property("text"))
        QTest.keyClick(self.window, Qt.Key_Return)
        QTest.qWait(40)
        self.assertEqual(self.window.activeFocusItem().property("text"), "Cancelar")
        QTest.keyClick(self.window, Qt.Key_Down)
        QTest.keyClick(self.window, Qt.Key_Return)
        QTest.qWait(40)
        self.assertTrue(self.b.controllerAutoApply)
        QTest.keyClick(self.window, Qt.Key_Escape)
        QTest.qWait(50)
        self.assertFalse(self.window.findChild(QObject, "controllerManager").property("opened"))
        self.assertEqual(self.b.page, 3)
        self.assertEqual(self.window.activeFocusItem().objectName(), "openControllerManager")

    def test_child_profile_cannot_expose_or_modify_personal_controller_profiles(self):
        self.b.store.set(
            "controller_profiles_v1",
            [
                dict(
                    id="x",
                    name="adult game name",
                    engine="dolphin",
                    family="joycon-r",
                    volatile=True,
                )
            ],
        )
        self.assertEqual(len(self.b.controllerProfiles), 1)
        self.b.setProfile("child")
        self.assertEqual(self.b.controllerProfiles, [])
        self.assertEqual(self.b.controllerDevices, [])
        self.assertEqual(self.b.controllerNotice, "")
        self.assertFalse(self.b.captureControllerProfile("/missing.ini", "dolphin", "joycon-r"))
        self.assertFalse(self.b.configureControllerTarget("/missing/WiimoteNew.ini"))
        self.b.navigate(3)
        QTest.qWait(40)
        self.click("settingsCategory-1")
        self.assertFalse(
            self.window.findChild(QObject, "openControllerManager").property("enabled")
        )
