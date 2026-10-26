"""Personal image cache. Decode raster images; never commit user imagery."""
import uuid
from pathlib import Path
from PySide6.QtGui import QImageReader
from .installed import local_path
class LocalArtwork:
    def __init__(self,library,root):self.library=library;self.root=Path(root);self.pending={}
    def discard(self):
        if self.pending:
            Path(self.pending['staged']).unlink(missing_ok=True);self.pending={}
    def prepare(self,game_id,role,value):
        if not self.library.raw(game_id) or role not in ['cover','backdrop']:raise ValueError("Juego o tipo de imagen no válido.")
        path=local_path(value)
        if path.suffix.lower() not in ['.png','.jpg','.jpeg','.webp'] or not path.is_file() or path.stat().st_size>20*1024*1024:raise ValueError("Usa PNG, JPG o WebP de hasta 20 MiB.")
        reader=QImageReader(str(path));size=reader.size()
        if size.width()<1 or size.height()<1 or max(size.width(),size.height())>8192 or size.width()*size.height()>32_000_000:raise ValueError("Imagen no válida o demasiado grande (8192 px / 32 MP).")
        image=reader.read()
        if image.isNull():raise ValueError("No se pudo decodificar la imagen.")
        self.discard();self.root.mkdir(parents=True,exist_ok=True)
        staged=self.root/(uuid.uuid4().hex+'.png')
        if not image.save(str(staged),'PNG'):raise ValueError("No se pudo guardar la imagen en la caché personal.")
        self.pending=dict(id=game_id,role=role,staged=str(staged),preview=staged.as_uri(),source=str(path),replacing=bool(self.library.raw(game_id)[role]))
        return self.pending
    def confirm(self):
        p=self.pending
        if not p:return
        if not self.library.raw(p['id']):self.discard();raise ValueError("Juego no encontrado.")
        # Only column names from the fixed enum above reach this statement.
        old=self.library.raw(p['id'])[p['role']]
        with self.library.store.db:self.library.store.db.execute('UPDATE real_games SET '+p['role']+'=? WHERE id=?',(p['staged'],p['id']))
        self.pending={}
        if old and Path(old).parent==self.root:Path(old).unlink(missing_ok=True)
