"""Raw-button learning and held system gesture, independent from navigation keys."""


class SystemGesture:
    def __init__(self, bridge, hold=0.8):
        self.bridge = bridge
        self.hold = hold
        self.since = None
        self.ready = False
        self.latched = False
        self.capturing = False

    def update(self, actions, now, reset=False):
        buttons = {x for x in actions if x.startswith("raw-") or x in ("guide", "view", "menu")}
        if self.bridge.shortcut_capture and not self.capturing:
            self.ready = False
            self.since = None
        self.capturing = self.bridge.shortcut_capture
        if reset:
            self.since = None
            self.ready = False
            self.latched = False
            return False
        if not buttons:
            self.ready = True
            self.latched = False
            self.since = None
            return False
        if not self.ready or self.latched:
            return False
        if self.bridge.shortcut_capture and "back" in actions:
            self.bridge.shortcut_capture = False
            self.bridge.shortcut_message = "Captura cancelada; atajo anterior conservado."
            self.bridge.operationChanged.emit()
            self.latched = True
            return True
        desired = set(self.bridge.store.get("quick_menu_buttons", ["view", "menu"]))
        capturing = self.bridge.shortcut_capture
        matches = capturing or "guide" in buttons or (desired and desired <= buttons)
        if not matches:
            self.since = None
            return False
        # The whole chord must remain unchanged for the hold period.
        marker = frozenset(buttons if capturing else ["guide"] if "guide" in buttons else desired)
        if not self.since or self.since[0] != marker:
            self.since = (marker, now)
        if now - self.since[1] >= self.hold:
            self.latched = True
            if capturing:
                self.bridge.save_quick_shortcut(buttons)
            elif self.bridge.launchBusy:
                if self.bridge.quick_menu.opened:
                    self.bridge.quick_menu.back()
                else:
                    self.bridge.quick_menu.open()
        return True
