"""Read-only SDL2 inventory. A GUID identifies a model, never a physical unit."""

import ctypes
import ctypes.util
import hashlib
import sys
from pathlib import Path


def family(name):
    value = name.casefold()
    if "joy-con" in value or "joycon" in value:
        if "(r)" in value or "right" in value:
            return "joycon-r"
        if "(l)" in value or "left" in value:
            return "joycon-l"
        return "joycon"
    if "dualsense" in value or "ps5 controller" in value:
        return "dualsense"
    if "xbox" in value or "xinput" in value:
        return "xbox"
    if "wiimote" in value or "nintendo rvl-cnt" in value:
        return "wiimote"
    return "other"


def physical_id(vendor, product, serial):
    if not serial:
        return ""
    material = f"{vendor:04x}:{product:04x}:{serial}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


class SDLInventory:
    def __init__(self, dolphin_executable=""):
        self.library = None
        self.xinput = None
        if sys.platform == "win32":
            from .gamepad import WindowsPad

            try:
                self.xinput = WindowsPad().xinput
            except OSError:
                pass
        self.initialized = False
        candidates = []
        if sys.platform == "win32" and dolphin_executable:
            candidates.append(str(Path(dolphin_executable).parent / "SDL2.dll"))
        candidate = ctypes.util.find_library("SDL2")
        if candidate:
            candidates.append(candidate)
        for candidate in candidates:
            try:
                self.library = ctypes.CDLL(candidate)
                break
            except OSError:
                continue
        self.error = ""
        if not self.library:
            self.error = "SDL2 no disponible; no se pueden identificar mandos mediante SDL."
            return
        try:
            lib = self.library
            lib.SDL_InitSubSystem.argtypes = [ctypes.c_uint32]
            lib.SDL_InitSubSystem.restype = ctypes.c_int
            lib.SDL_NumJoysticks.restype = ctypes.c_int
            lib.SDL_JoystickNameForIndex.argtypes = [ctypes.c_int]
            lib.SDL_JoystickNameForIndex.restype = ctypes.c_char_p
            lib.SDL_JoystickOpen.argtypes = [ctypes.c_int]
            lib.SDL_JoystickOpen.restype = ctypes.c_void_p
            lib.SDL_JoystickClose.argtypes = [ctypes.c_void_p]
            for fn in ("SDL_JoystickGetDeviceVendor", "SDL_JoystickGetDeviceProduct"):
                f = getattr(lib, fn)
                f.argtypes = [ctypes.c_int]
                f.restype = ctypes.c_uint16
            if hasattr(lib, "SDL_JoystickGetSerial"):
                lib.SDL_JoystickGetSerial.argtypes = [ctypes.c_void_p]
                lib.SDL_JoystickGetSerial.restype = ctypes.c_char_p
            self.sensor_api = all(
                hasattr(lib, name)
                for name in (
                    "SDL_IsGameController",
                    "SDL_GameControllerOpen",
                    "SDL_GameControllerHasSensor",
                    "SDL_GameControllerClose",
                )
            )
            if self.sensor_api:
                lib.SDL_IsGameController.argtypes = [ctypes.c_int]
                lib.SDL_IsGameController.restype = ctypes.c_int
                lib.SDL_GameControllerOpen.argtypes = [ctypes.c_int]
                lib.SDL_GameControllerOpen.restype = ctypes.c_void_p
                lib.SDL_GameControllerHasSensor.argtypes = [ctypes.c_void_p, ctypes.c_int]
                lib.SDL_GameControllerHasSensor.restype = ctypes.c_int
                lib.SDL_GameControllerClose.argtypes = [ctypes.c_void_p]
            lib.SDL_SetHint.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
            lib.SDL_SetHint(b"SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", b"1")
            if lib.SDL_InitSubSystem(0x2200) != 0:
                raise RuntimeError("SDL no pudo inicializar el subsistema de mandos.")
            self.initialized = True
        except (AttributeError, RuntimeError) as exc:
            self.library = None
            self.error = str(exc)

    def close(self):
        if self.library and self.initialized:
            self.library.SDL_QuitSubSystem(0x2200)
            self.initialized = False

    def __del__(self):
        self.close()

    def devices(self):
        results = []
        if self.xinput:
            from .gamepad import State

            for index in range(4):
                state = State()
                if self.xinput(index, ctypes.byref(state)) == 0:
                    results.append(
                        dict(
                            name=f"XInput mando {index + 1}",
                            family="xinput",
                            vendor=0,
                            product=0,
                            device_id="",
                            stable=False,
                            backend="XInput",
                            connection="desconocida",
                            sensors="no verificado",
                            warning="Índice temporal; puede duplicar un mando SDL o Steam Input.",
                        )
                    )
        if not self.library:
            return results
        lib = self.library
        lib.SDL_JoystickUpdate()
        for index in range(max(0, lib.SDL_NumJoysticks())):
            raw = lib.SDL_JoystickNameForIndex(index) or b"Mando desconocido"
            name = raw.decode("utf-8", "replace")
            vendor = int(lib.SDL_JoystickGetDeviceVendor(index))
            product = int(lib.SDL_JoystickGetDeviceProduct(index))
            handle = lib.SDL_JoystickOpen(index)
            serial = b""
            if handle:
                if hasattr(lib, "SDL_JoystickGetSerial"):
                    serial = lib.SDL_JoystickGetSerial(handle) or b""
                lib.SDL_JoystickClose(handle)
            serial = serial.decode("utf-8", "replace")
            sensors = "no verificado"
            if self.sensor_api and lib.SDL_IsGameController(index):
                controller = lib.SDL_GameControllerOpen(index)
                if controller:
                    try:
                        accel = any(
                            lib.SDL_GameControllerHasSensor(controller, n) for n in (1, 3, 5)
                        )
                        gyro = any(
                            lib.SDL_GameControllerHasSensor(controller, n) for n in (2, 4, 6)
                        )
                        sensors = (
                            "acelerómetro "
                            + ("disponible" if accel else "no reportado")
                            + ", giroscopio "
                            + ("disponible" if gyro else "no reportado")
                        )
                    finally:
                        lib.SDL_GameControllerClose(controller)
            results.append(
                dict(
                    name=name,
                    family=family(name),
                    vendor=vendor,
                    product=product,
                    device_id=physical_id(vendor, product, serial),
                    stable=bool(serial),
                    backend="SDL",
                    connection="desconocida",
                    sensors=sensors,
                )
            )
        return results
