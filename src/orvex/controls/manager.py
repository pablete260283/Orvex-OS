"""Controller snapshots and bindings stored in ORVEX, never in emulator profiles."""

import configparser
import hashlib
import re
import uuid
import os
import sqlite3
import stat
import sys
import tempfile
from pathlib import Path


def engine_for(store, game_id):
    for table, engine in [("dolphin_roms", "dolphin"), ("pcsx2_roms", "pcsx2")]:
        exists = store.db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if (
            exists
            and store.db.execute(f"SELECT 1 FROM {table} WHERE game_id=?", (game_id,)).fetchone()
        ):
            return engine
    return "native"


def digest(data):
    return hashlib.sha256(data).hexdigest()


class ControllerManager:
    def __init__(self, store, library, root, inventory):
        self.store = store
        self.library = library
        self.root = Path(root)
        self.inventory = inventory
        self.notice = ""
        self.active_transaction = None
        self.recovery = self.recover()

    def profiles(self):
        return self.store.get("controller_profiles_v1", [])

    def bindings(self):
        return self.store.get("controller_bindings_v1", [])

    def capture(self, path, name, engine, family):
        source = Path(path).expanduser()
        if (
            not source.is_absolute()
            or source.is_symlink()
            or not source.is_file()
            or source.suffix.lower() != ".ini"
        ):
            raise ValueError("Selecciona un archivo INI existente mediante una ruta absoluta.")
        if source.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("El archivo de perfil supera 2 MiB.")
        data = source.read_bytes()
        if not data or len(data) > 2 * 1024 * 1024 or b"\0" in data:
            raise ValueError("El archivo de perfil está vacío o supera 2 MiB.")
        try:
            text = data.decode("utf-8-sig")
            parser = configparser.RawConfigParser(interpolation=None, strict=False)
            parser.read_string(text)
        except (UnicodeError, configparser.Error) as error:
            raise ValueError("El archivo no es un INI de texto válido.") from error
        if (
            not parser.sections()
            or not name.strip()
            or engine not in ("dolphin", "pcsx2", "native")
        ):
            raise ValueError("Indica un nombre y un motor válidos para el perfil.")
        self.root.mkdir(parents=True, exist_ok=True)
        identifier = uuid.uuid4().hex
        destination = self.root / (identifier + ".ini")
        with destination.open("xb") as output:
            output.write(data)
        profile = dict(
            id=identifier,
            name=name.strip(),
            engine=engine,
            family=family,
            sha256=digest(data),
            snapshot=str(destination),
            source=str(source),
            sections=parser.sections(),
            volatile=bool(re.search(r"SDL/\d+/", text, re.I)),
        )
        try:
            self.store.set("controller_profiles_v1", self.profiles() + [profile])
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return profile

    def bind(self, profile_id, scope, game_id, platform, engine, device_id, family, player):
        profile = next((p for p in self.profiles() if p["id"] == profile_id), None)
        if (
            not profile
            or scope not in ("game", "platform", "default")
            or engine != profile["engine"]
        ):
            raise ValueError("Perfil o motor incompatible.")
        if family != profile["family"] or not device_id:
            raise ValueError("Selecciona un mando identificado individualmente y compatible.")
        if player not in range(1, 5):
            raise ValueError("Jugador fuera de rango.")
        game = self.library.raw(game_id) if scope == "game" else None
        if scope == "game" and (not game or engine_for(self.store, game_id) != engine):
            raise ValueError("El juego o su motor no coinciden con el perfil.")
        if scope == "platform" and not platform.strip():
            raise ValueError("Selecciona una plataforma.")
        binding = dict(
            profile_id=profile_id,
            scope=scope,
            game_id=game_id if game else "",
            platform=platform.strip() if scope == "platform" else "",
            engine=engine,
            device_id=device_id,
            family=family,
            player=player,
        )
        old = self.bindings()
        key = ("scope", "game_id", "platform", "engine", "device_id", "player")
        old = [b for b in old if any(b[k] != binding[k] for k in key)]
        self.store.set("controller_bindings_v1", old + [binding])

    def select(self, game_id, devices):
        game = self.library.raw(game_id)
        if not game:
            raise ValueError("Juego no encontrado.")
        engine = engine_for(self.store, game_id)
        profiles = {p["id"]: p for p in self.profiles()}
        candidates = []
        for device in devices:
            # XInput can be a Steam Input virtual device representing any SDL
            # controller, so do not guess which physical unit it duplicates.
            if device.get("backend") == "SDL" and any(
                d.get("backend") == "XInput" for d in devices
            ):
                continue
            if not device.get("device_id") or not device.get("stable"):
                continue
            # A duplicate serial is ambiguous, even if an API claims it is stable.
            if sum(d.get("device_id") == device["device_id"] for d in devices) != 1:
                continue
            for binding in self.bindings():
                if (
                    binding["device_id"] != device["device_id"]
                    or binding["family"] != device["family"]
                    or binding["engine"] != engine
                ):
                    continue
                score = {"default": 1, "platform": 2, "game": 3}[binding["scope"]]
                if binding["scope"] == "game" and binding["game_id"] != game_id:
                    continue
                if binding["scope"] == "platform" and binding["platform"] != game["platform"]:
                    continue
                profile = profiles.get(binding["profile_id"])
                if profile:
                    candidates.append((binding["player"], score, profile))
        chosen = []
        for player in range(1, 5):
            player_candidates = [c for c in candidates if c[0] == player]
            if not player_candidates:
                continue
            best = max(c[1] for c in player_candidates)
            winners = [c for c in player_candidates if c[1] == best]
            if len(winners) == 1:
                chosen.append(dict(player=player, profile=winners[0][2], scope_score=best))
        return chosen

    def configure_target(self, path):
        target = Path(path).expanduser()
        if (
            not target.is_absolute()
            or target.is_symlink()
            or not target.is_file()
            or target.name.lower() != "wiimotenew.ini"
        ):
            raise ValueError("Selecciona el archivo WiimoteNew.ini existente de Dolphin.")
        self.store.set("controller_target_dolphin", str(target.resolve()))

    def apply_for_launch(self, game_id, selected):
        """Explicitly enabled full-config snapshots only; no profile conversion."""
        if not self.store.get("controller_apply_enabled", False) or not selected:
            return False
        if (
            engine_for(self.store, game_id) != "dolphin"
            or len(selected) != 1
            or selected[0]["player"] != 1
        ):
            self.notice += " No se aplica: motor o jugadores no admitidos automáticamente."
            return False
        profile = selected[0]["profile"]
        if profile["volatile"] or "Wiimote1" not in profile["sections"]:
            self.notice += (
                " No se aplica: contiene índice SDL variable o no es WiimoteNew.ini completo."
            )
            return False
        if self.store.get("controller_restore_journal", {}):
            self.notice += " Hay una recuperación pendiente; revisa Diagnóstico."
            return False
        target = Path(self.store.get("controller_target_dolphin", ""))
        if (
            not target.is_absolute()
            or target.is_symlink()
            or not target.is_file()
            or target.name.lower() != "wiimotenew.ini"
        ):
            self.notice += " Falta seleccionar WiimoteNew.ini en Configuración."
            return False
        snapshot = Path(profile["snapshot"])
        content = snapshot.read_bytes()
        if digest(content) != profile["sha256"]:
            raise ValueError("La copia aprobada del perfil cambió; no se modificó Dolphin.")
        original = target.read_bytes()
        if len(original) > 2 * 1024 * 1024:
            raise ValueError("Configuración Dolphin demasiado grande.")
        self.root.mkdir(parents=True, exist_ok=True)
        backup = self.root / ("backup-" + uuid.uuid4().hex + ".ini")
        with backup.open("xb") as stream:
            stream.write(original)
            stream.flush()
            os.fsync(stream.fileno())
        transaction_id = uuid.uuid4().hex
        journal = dict(
            transaction_id=transaction_id,
            target=str(target),
            backup=str(backup),
            original=digest(original),
            applied=digest(content),
            phase="prepared",
        )
        self.store.set("controller_restore_journal", journal)
        self.active_transaction = transaction_id
        if digest(target.read_bytes()) != journal["original"]:
            raise ValueError(
                "La configuración Dolphin cambió durante el respaldo; no se aplicó el perfil."
            )
        self._atomic_replace(target, content)
        self.notice = "Perfil aplicado temporalmente; copia de seguridad guardada."
        return True

    @staticmethod
    def _atomic_replace(target, content):
        fd, name = tempfile.mkstemp(prefix=".orvex-", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as output:
                output.write(content)
                output.flush()
                os.fsync(output.fileno())
            os.chmod(name, stat.S_IMODE(target.stat().st_mode))
            os.replace(name, target)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def mark_starting(self):
        journal = self.store.get("controller_restore_journal", {})
        if self.active_transaction and journal.get("transaction_id") == self.active_transaction:
            journal["phase"] = "starting"
            self.store.set("controller_restore_journal", journal)

    def mark_running(self, pid):
        journal = self.store.get("controller_restore_journal", {})
        if self.active_transaction and journal.get("transaction_id") == self.active_transaction:
            journal["phase"] = "running"
            journal["pid"] = int(pid)
            try:
                self.store.set("controller_restore_journal", journal)
            except sqlite3.Error:
                self.recovery = "No se pudo guardar el proceso; recuperación manual pendiente."

    @staticmethod
    def _process_running(pid):
        if not isinstance(pid, int) or pid <= 0:
            return True
        if sys.platform == "win32":
            import ctypes

            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
            kernel.OpenProcess.restype = ctypes.c_void_p
            kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            handle = kernel.OpenProcess(0x1000, False, pid)
            if not handle:
                return ctypes.get_last_error() != 87  # invalid PID; any other failure is uncertain
            try:
                status = ctypes.c_uint32()
                return (
                    not kernel.GetExitCodeProcess(handle, ctypes.byref(status))
                    or status.value == 259
                )
            finally:
                kernel.CloseHandle(handle)
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except OSError:
            return True

    def finish_launch(self):
        transaction_id = self.active_transaction
        try:
            if not transaction_id:
                return self.recovery
            return self.recover(finished_transaction=transaction_id)
        finally:
            self.active_transaction = None

    def recover(self, finished_transaction=None, confirmed_stopped=False):
        journal = self.store.get("controller_restore_journal", {})
        if not journal:
            return "Sin cambios pendientes en configuraciones de emulador."
        try:
            owned_finished = bool(finished_transaction) and (
                finished_transaction == self.active_transaction == journal.get("transaction_id")
            )
            if finished_transaction and not owned_finished:
                raise ValueError(
                    "El respaldo pertenece a otro lanzamiento; no se modificó el destino."
                )
            if not owned_finished and (
                (journal.get("phase") == "starting" and not confirmed_stopped)
                or (journal.get("phase") == "running" and self._process_running(journal.get("pid")))
            ):
                raise ValueError(
                    "El emulador podría seguir abierto; conserva el respaldo y vuelve a intentar cuando termine."
                )
            target = Path(journal["target"])
            backup = Path(journal["backup"])
            if (
                target.is_symlink()
                or backup.is_symlink()
                or backup.parent != self.root
                or not target.is_file()
            ):
                raise ValueError("No se pudo verificar el destino o la copia de seguridad.")
            current = digest(target.read_bytes())
            if current == journal["original"]:
                self.store.set("controller_restore_journal", {})
                return "La configuración original ya estaba presente."
            if current != journal["applied"]:
                raise ValueError(
                    "Dolphin cambió el archivo durante la sesión; se conservaron ambos archivos."
                )
            data = backup.read_bytes()
            if digest(data) != journal["original"]:
                raise ValueError("La copia de seguridad no coincide; no se modificó el destino.")
            self._atomic_replace(target, data)
            self.store.set("controller_restore_journal", {})
            return "Configuración original restaurada desde copia de seguridad."
        except (OSError, ValueError, KeyError, sqlite3.Error) as error:
            return "Recuperación pendiente: " + str(error)

    def prepare_for_launch(self, game_id):
        try:
            devices = self.inventory.devices()
            selected = self.select(game_id, devices)
            if selected:
                names = ", ".join(f"J{p['player']}: {p['profile']['name']}" for p in selected)
                self.notice = f"Perfiles seleccionados: {names}."
                if not self.apply_for_launch(game_id, selected):
                    self.notice += " Se mantiene la configuración del emulador."
            elif not devices:
                self.notice = "Sin mando detectado: se conserva la configuración existente."
            else:
                self.notice = (
                    "Sin perfil inequívoco para este mando: se conserva la configuración existente."
                )
            return selected
        except (OSError, ValueError, KeyError, sqlite3.Error) as error:
            self.notice = (
                "No se pudo aplicar el perfil; configuración existente conservada: " + str(error)
            )
            self.recovery = self.recover()
            return []
