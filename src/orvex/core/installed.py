"""Persistent, manually imported native games. Never executes during import."""
import hashlib,os,sys,uuid
from datetime import datetime,timezone
from pathlib import Path
from PySide6.QtCore import QUrl
from .artwork import resolve_art

def utc_now():return datetime.now(timezone.utc).isoformat(timespec="milliseconds")
def local_path(value):
    url=QUrl(value)
    if url.isLocalFile():value=url.toLocalFile()
    elif "://" in value:raise ValueError("Selecciona un archivo local, no una URL.")
    path=Path(value).expanduser()
    if not path.is_absolute():raise ValueError("La ruta debe ser absoluta.")
    return path.resolve(strict=True)
def validate_executable(value):
    try:path=local_path(value)
    except (OSError,ValueError,RuntimeError) as e:raise ValueError("Ruta no válida o archivo inexistente.") from e
    if not path.is_file():raise ValueError("La ruta debe apuntar a un archivo.")
    if path.stat().st_size>512*1024*1024:raise ValueError("Ejecutable demasiado grande para esta primera versión (máximo 512 MiB).")
    with path.open("rb") as f:magic=f.read(4)
    if sys.platform=="win32":
        if path.suffix.lower()!=".exe" or magic[:2]!=b"MZ":raise ValueError("Selecciona un ejecutable Windows .exe; no se admiten accesos directos ni scripts.")
    elif sys.platform.startswith("linux"):
        if magic!=b"\x7fELF" or not os.access(path,os.X_OK):raise ValueError("Selecciona un ejecutable Linux ELF con permiso de ejecución. No se admiten scripts ni .exe de Windows.")
    else:raise ValueError("Lanzamiento disponible únicamente en Windows y Linux.")
    digest=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):digest.update(block)
    return str(path),digest.hexdigest()
class InstalledLibrary:
    def __init__(self,store):self.store=store
    def import_game(self,name,platform,value):
        name=name.strip();platform=platform.strip()
        if not name or len(name)>120 or not platform or len(platform)>80:raise ValueError("Indica nombre (máximo 120 caracteres) y plataforma (máximo 80).")
        executable,_=validate_executable(value)
        if self.store.db.execute("SELECT 1 FROM real_games WHERE executable=?",(executable,)).fetchone():raise ValueError("Este ejecutable ya está en la biblioteca.")
        game_id="local-"+uuid.uuid4().hex
        with self.store.db:self.store.db.execute("INSERT INTO real_games(id,name,platform,executable,created_at) VALUES(?,?,?,?,?)",(game_id,name,platform,executable,utc_now()))
        return game_id
    def raw(self,game_id):
        cursor=self.store.db.execute("SELECT * FROM real_games WHERE id=?",(game_id,))
        row=cursor.fetchone()
        return dict(zip([column[0] for column in cursor.description],row)) if row else {}
    def games(self,profile="adult"):
        # Imported titles have unknown age; fail closed for the child demonstration.
        if profile!="adult":return []
        result=[]
        for (game_id,) in self.store.db.execute("SELECT id FROM real_games ORDER BY created_at DESC,id"):
            e=self.raw(game_id)
            elapsed_ms,last=self.store.db.execute("SELECT COALESCE(SUM(duration_ms),0),MAX(started_at) FROM play_sessions WHERE game_id=?",(game_id,)).fetchone()
            seconds=elapsed_ms/1000
            last_label=datetime.fromisoformat(last).astimezone().strftime("%d-%m-%Y %H:%M %Z") if last else "Sin sesiones"
            progress=dict(source="observed",percent=None,verifiedPercent=False,timeLabel=f"{int(seconds//3600)} h {int(seconds//60)%60} min {seconds%60:.1f} s",lastLabel=last_label,last_session=last,statusLabel="Sesiones registradas" if last else "Sin sesiones",percentLabel="Avance no disponible")
            result.append(dict(id=game_id,title=e['name'],platform=e['platform'],kind="game",age=None,catalog_source="installed",installed=True,art="aurora",cover_url=Path(e['cover']).as_uri() if e['cover'] and Path(e['cover']).is_file() else resolve_art('aurora'),backdrop_url=Path(e['backdrop']).as_uri() if e['backdrop'] and Path(e['backdrop']).is_file() else resolve_art('aurora','backdrop'),description="Juego importado en tu biblioteca personal.",availability=e['executable'],progress=progress,favorite=game_id in self.store.favorites(profile)))
        return result
