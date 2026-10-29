"""Read a mapped SDL2 controller, including GUIDE only when SDL exposes it.

Reuses ORVEX's existing SDL instance; never downloads DLLs or changes emulator mappings.
"""

import ctypes as c


class SDLNavigation:
    def __init__(self, inventory, fallback):
        self.inventory = inventory
        self.fallback = fallback
        self.handle = None
        self.connection_token = 0
        self.fallback_token = None
        self.lib = inventory.library
        if not self.lib:
            return
        signatures = {
            "SDL_GameControllerOpen": ([c.c_int], c.c_void_p),
            "SDL_IsGameController": ([c.c_int], c.c_int),
            "SDL_GameControllerGetAttached": ([c.c_void_p], c.c_int),
            "SDL_GameControllerGetButton": ([c.c_void_p, c.c_int], c.c_uint8),
            "SDL_GameControllerGetAxis": ([c.c_void_p, c.c_int], c.c_int16),
            "SDL_GameControllerClose": ([c.c_void_p], None),
        }
        try:
            for name, (args, result) in signatures.items():
                function = getattr(self.lib, name)
                function.argtypes, function.restype = args, result
        except AttributeError:
            self.lib = None

    def close(self):
        if self.handle and self.lib:
            self.lib.SDL_GameControllerClose(self.handle)
        self.handle = None

    def read(self):
        if self.lib:
            self.lib.SDL_GameControllerUpdate()
            if self.handle and not self.lib.SDL_GameControllerGetAttached(self.handle):
                self.close()
                self.connection_token += 1
            if not self.handle:
                for i in range(max(0, self.lib.SDL_NumJoysticks())):
                    if self.lib.SDL_IsGameController(i):
                        self.handle = self.lib.SDL_GameControllerOpen(i)
                        if self.handle:
                            self.connection_token += 1
                            break
            if self.handle:
                actions = set()
                mapping = {
                    0: "confirm",
                    1: "back",
                    4: "view",
                    5: "guide",
                    6: "menu",
                    11: "up",
                    12: "down",
                    13: "left",
                    14: "right",
                }
                for button in range(21):
                    if self.lib.SDL_GameControllerGetButton(self.handle, button):
                        actions.add("raw-" + str(button))
                        if button in mapping:
                            actions.add(mapping[button])
                x = self.lib.SDL_GameControllerGetAxis(self.handle, 0)
                y = self.lib.SDL_GameControllerGetAxis(self.handle, 1)
                if abs(x) > 16000:
                    actions.add("right" if x > 0 else "left")
                if abs(y) > 16000:
                    actions.add("down" if y > 0 else "up")
                return actions
        actions = self.fallback.read() if self.fallback else set()
        token = getattr(self.fallback, "connection_token", None)
        if token != self.fallback_token:
            self.fallback_token = token
            self.connection_token += 1
        return actions
