"""Confirmed direct-process launching, never a shell command."""

import json
import sqlite3
import time
from pathlib import Path

from PySide6.QtCore import QObject, Property, QProcess, Signal, Slot

from .installed import utc_now, validate_arguments, validate_executable


class GameLauncher(QObject):
    changed = Signal()

    def __init__(self, library, parent=None):
        super().__init__(parent)
        self.library = library
        self.store = library.store
        self.pending = {}
        self.message = ""
        self.state = "Disponible"
        self.process = None
        self.session_id = None
        self.started = None
        self.game_id = ""
        self.record_error = ""

    @Property(bool, notify=changed)
    def busy(self):
        return self.process is not None

    def request(self, game_id):
        if self.busy:
            self.message = "Ya hay un proceso supervisado en ejecución."
            self.changed.emit()
            return
        self.pending = {}
        self.state = "Preparando"
        self.changed.emit()
        try:
            game = self.library.raw(game_id)
            if not game:
                raise ValueError("Juego no encontrado.")
            from ..adapters.registry import resolve
            resolved=resolve(self.store,game_id)
            if resolved:
                game['executable']=resolved[0];game['arguments']=json.dumps(resolved[1])
            path, digest = validate_executable(game["executable"])
            arguments = validate_arguments(game["arguments"])
            if game["trusted_hash"] != digest or game["trusted_arguments"] != arguments:
                self.pending = dict(
                    id=game_id, title=game["name"], path=path, digest=digest, arguments=arguments
                )
                self.message = "Confirma este ejecutable y sus parámetros antes de iniciarlo."
            else:
                self._start(game_id, path, digest, arguments)
        except (OSError, ValueError, sqlite3.Error) as error:
            self.state = "Error"
            self.message = str(error)
        self.changed.emit()

    @Slot()
    def cancel(self):
        if self.pending:
            self.pending = {}
            self.state = "Disponible"
            self.message = "Operación cancelada. No se ejecutó ningún archivo."
        self.changed.emit()

    @Slot()
    def confirm(self):
        pending = self.pending
        self.pending = {}
        if not pending or self.busy:
            self.changed.emit()
            return
        try:
            game = self.library.raw(pending["id"])
            from ..adapters.registry import resolve
            resolved=resolve(self.store,pending['id'])
            if resolved:game['executable']=resolved[0];game['arguments']=json.dumps(resolved[1])
            path, digest = validate_executable(game["executable"])
            arguments = validate_arguments(game["arguments"])
            if (
                digest != pending["digest"]
                or path != pending["path"]
                or arguments != pending["arguments"]
            ):
                raise ValueError(
                    "El archivo o sus parámetros cambió: vuelve a solicitar el lanzamiento para revisarlo."
                )
            self._start(pending["id"], path, digest, arguments)
        except (OSError, ValueError, KeyError, sqlite3.Error) as error:
            self.state = "Error"
            self.message = str(error)
        self.changed.emit()

    def _start(self, game_id, path, digest, arguments):
        self.game_id = game_id
        self.started = None
        self.session_id = None
        self.record_error = ""
        self.state = "Preparando"
        process = QProcess(self)
        self.process = process
        process.setWorkingDirectory(str(Path(path).parent))
        process.setStandardOutputFile(QProcess.nullDevice())
        process.setStandardErrorFile(QProcess.nullDevice())

        def began():
            self.started = time.monotonic()
            self.state = "Ejecutando"
            try:
                with self.store.db:
                    self.store.db.execute(
                        "UPDATE real_games SET trusted_hash=?,trusted_arguments=? WHERE id=?",
                        (digest, arguments, game_id),
                    )
                    cursor = self.store.db.execute(
                        "INSERT INTO play_sessions(game_id,started_at,status) VALUES(?,?,'running')",
                        (game_id, utc_now()),
                    )
                    self.session_id = cursor.lastrowid
            except sqlite3.Error as error:
                self.record_error = str(error)
            self.message = (
                "En ejecución. No se pudo registrar la sesión: " + self.record_error
                if self.record_error
                else "En ejecución. ORVEX registra la duración del proceso directo."
            )
            self.changed.emit()

        process.started.connect(began)
        process.finished.connect(self._finished)
        process.errorOccurred.connect(self._error)
        self.message = "Iniciando…"
        process.start(path, json.loads(arguments))

    def _error(self, error):
        if error == QProcess.FailedToStart:
            self.state = "Error"
            self.message = "No se pudo iniciar el ejecutable: " + self.process.errorString()
            self._release()
            self.changed.emit()

    def _finished(self, code, status):
        elapsed = (
            max(0, int((time.monotonic() - self.started) * 1000)) if self.started is not None else 0
        )
        normal = status == QProcess.NormalExit and code == 0
        self.state = "Finalizado" if normal else "Error"
        try:
            if self.session_id is not None:
                with self.store.db:
                    self.store.db.execute(
                        "UPDATE play_sessions SET ended_at=?,duration_ms=?,status=?,exit_code=? WHERE id=?",
                        (
                            utc_now(),
                            elapsed,
                            "finished" if normal else "error",
                            code,
                            self.session_id,
                        ),
                    )
        except sqlite3.Error as error:
            self.record_error = str(error)
        if self.record_error:
            self.state = "Error"
            self.message = "Proceso finalizado; no se pudo guardar la sesión: " + self.record_error
        else:
            self.message = f"Proceso finalizado · código {code} · {elapsed / 1000:.1f} s registrados. Si inició otro proceso, su tiempo no se puede deducir."
        self._release()
        self.changed.emit()

    def _release(self):
        process = self.process
        self.process = None
        self.session_id = None
        self.started = None
        if process:
            process.deleteLater()
