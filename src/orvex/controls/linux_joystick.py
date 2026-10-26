"""Read-only joydev input; no permissions or driver configuration changes."""

import os
import struct
import time
from pathlib import Path


class LinuxJoystick:
    def __init__(self):
        self.fd = None
        self.axes = {}
        self.buttons = {}
        self.retry = 0

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
        self.fd = None
        self.axes.clear()
        self.buttons.clear()

    def consume(self, data):
        _, value, kind, index = struct.unpack("=IhBB", data)
        kind &= 0x7F
        if kind == 1:
            self.buttons[index] = value
        elif kind == 2:
            self.axes[index] = value

    def read(self):
        if self.fd is None:
            if time.monotonic() < self.retry:
                return set()
            self.retry = time.monotonic() + 1
            for path in sorted(Path("/dev/input").glob("js*")):
                try:
                    self.fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                    break
                except OSError:
                    continue
            if self.fd is None:
                return set()
        try:
            for _ in range(128):
                data = os.read(self.fd, 8)
                if len(data) != 8:
                    self.close()
                    return set()
                self.consume(data)
        except BlockingIOError:
            pass
        except OSError:
            self.close()
            return set()
        actions = set()
        if self.buttons.get(0):
            actions.add("confirm")
        if self.buttons.get(1):
            actions.add("back")
        for axis, negative, positive in [
            (0, "left", "right"),
            (1, "up", "down"),
            (6, "left", "right"),
            (7, "up", "down"),
        ]:
            value = self.axes.get(axis, 0)
            if abs(value) > 16000:
                actions.add(positive if value > 0 else negative)
        return actions
