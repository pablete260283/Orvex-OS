"""Documented Win32 window messages only. Never suspend or kill a process."""

import ctypes
import sys
from ctypes import wintypes


class WindowControl:
    def __init__(self):
        self.api = None
        if sys.platform != "win32":
            return
        api = ctypes.WinDLL("user32", use_last_error=True)
        api.GetForegroundWindow.restype = wintypes.HWND
        api.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        api.IsWindow.argtypes = [wintypes.HWND]
        api.IsWindowVisible.argtypes = [wintypes.HWND]
        api.SetForegroundWindow.argtypes = [wintypes.HWND]
        api.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        self.callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        api.EnumWindows.argtypes = [self.callback_type, wintypes.LPARAM]
        self.api = api

    def owner(self, handle):
        if not self.api or not handle or not self.api.IsWindow(handle):
            return 0
        pid = wintypes.DWORD()
        self.api.GetWindowThreadProcessId(handle, ctypes.byref(pid))
        return pid.value

    def find(self, pid):
        if not self.api or not pid:
            return 0
        foreground = self.api.GetForegroundWindow()
        if self.owner(foreground) == pid:
            return foreground
        found = []

        @self.callback_type
        def visit(handle, _):
            if self.owner(handle) == pid and self.api.IsWindowVisible(handle):
                found.append(handle)
            return True

        self.api.EnumWindows(visit, 0)
        return found[0] if found else 0

    def focus(self, handle, pid):
        return bool(self.api and self.owner(handle) == pid and self.api.SetForegroundWindow(handle))

    def request_close(self, handle, pid):
        # The application owns its save/confirmation flow. No timeout -> kill escalation.
        return bool(
            self.api and self.owner(handle) == pid and self.api.PostMessageW(handle, 0x0010, 0, 0)
        )
