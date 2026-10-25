"""Explicit, confirmed direct-process launching without a shell or injected arguments."""
import time
from pathlib import Path
from PySide6.QtCore import QObject,QProcess,Signal,Property,Slot
from .installed import validate_executable,utc_now
class Launcher(QObject):
    changed=Signal()
    def __init__(self,library,parent=None):
        super().__init__(parent);self.library=library;self.store=library.store
        self.pending={};self.message="";self.process=None;self.session_id=None;self.started=None;self.game_id=""
    @Property(bool,notify=changed)
    def busy(self):return self.process is not None
    def request(self,game_id):
        self.pending={}
        if self.busy:self.message="Ya hay un proceso supervisado en ejecución.";self.changed.emit();return
        try:
            game=self.library.raw(game_id)
            if not game:raise ValueError("Juego no encontrado.")
            path,digest=validate_executable(game['executable'])
            if game['trusted_hash']!=digest:
                self.pending=dict(id=game_id,title=game['name'],path=path,digest=digest)
                self.message="Confirma el primer lanzamiento de este archivo. Importar no demuestra que sea seguro."
            else:self._start(game_id,path,digest)
        except (OSError,ValueError) as e:self.message=str(e)
        self.changed.emit()
    @Slot()
    def cancel(self):
        had_pending=bool(self.pending);self.pending={}
        if had_pending:self.message="Operación cancelada. No se ejecutó ningún archivo."
        self.changed.emit()
    @Slot()
    def confirm(self):
        pending=self.pending;self.pending={}
        if not pending or self.busy:self.changed.emit();return
        try:
            game=self.library.raw(pending['id']);path,digest=validate_executable(game['executable'])
            if digest!=pending['digest'] or path!=pending['path']:raise ValueError("El archivo cambió: vuelve a solicitar el lanzamiento para revisarlo.")
            self._start(pending['id'],path,digest)
        except (OSError,ValueError,KeyError) as e:self.message=str(e)
        self.changed.emit()
    def _start(self,game_id,path,digest):
        self.game_id=game_id;self.started=None;self.session_id=None
        p=QProcess(self);self.process=p
        p.setWorkingDirectory(str(Path(path).parent))
        p.setStandardOutputFile(QProcess.nullDevice());p.setStandardErrorFile(QProcess.nullDevice())
        def began():
            self.started=time.monotonic()
            with self.store.db:
                self.store.db.execute("UPDATE real_games SET trusted_hash=? WHERE id=?",(digest,game_id))
                cursor=self.store.db.execute("INSERT INTO play_sessions(game_id,started_at,status) VALUES(?,?,'running')",(game_id,utc_now()))
                self.session_id=cursor.lastrowid
            self.message="En ejecución. ORVEX registra la duración del proceso directo.";self.changed.emit()
        p.started.connect(began)
        p.finished.connect(self._finished)
        p.errorOccurred.connect(self._error)
        self.message="Iniciando…";p.start(path,[])
    def _error(self,error):
        if error==QProcess.FailedToStart:
            self.message="No se pudo iniciar el ejecutable: "+self.process.errorString();self._release();self.changed.emit()
    def _finished(self,code,status):
        elapsed=max(0,int((time.monotonic()-self.started)*1000)) if self.started is not None else 0
        if self.session_id is not None:
            result="finished" if status==QProcess.NormalExit and code==0 else "error"
            with self.store.db:self.store.db.execute("UPDATE play_sessions SET ended_at=?,duration_ms=?,status=?,exit_code=? WHERE id=?",(utc_now(),elapsed,result,code,self.session_id))
        self.message=f"Proceso finalizado · código {code} · {elapsed/1000:.1f} s registrados. Si inició otro proceso, su tiempo no se puede deducir."
        self._release();self.changed.emit()
    def _release(self):
        p=self.process;self.process=None;self.session_id=None;self.started=None
        if p:p.deleteLater()
