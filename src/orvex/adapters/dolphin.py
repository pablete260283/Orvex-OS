"""Dolphin folder indexing and direct command construction. Never boots during scan."""
import json
import os
import shutil
import uuid
from pathlib import Path
from orvex.core.installed import utc_now, validate_executable

FORMATS = {'.iso', '.gcm', '.gcz', '.rvz', '.wia', '.wbfs', '.ciso'}

class DolphinAdapter:
    key = 'dolphin'
    table = 'dolphin_roms'
    platforms = ['Wii', 'GameCube']
    formats = FORMATS
    names = ['dolphin', 'dolphin-emu']
    flags = ['--batch', '--exec']
    def __init__(self, store):
        self.store = store
        self.store.db.execute(f'CREATE TABLE IF NOT EXISTS {self.table}(game_id TEXT PRIMARY KEY,path TEXT UNIQUE NOT NULL)')
        self.store.db.commit()

    def detect(self):
        candidates = [shutil.which('Dolphin.exe'), shutil.which('dolphin-emu')]
        for variable in ['ProgramFiles', 'ProgramFiles(x86)', 'LOCALAPPDATA']:
            if os.environ.get(variable):
                candidates.append(str(Path(os.environ[variable])/'Dolphin'/'Dolphin.exe'))
        configured = self.store.get(self.key+'_executable', '')
        if configured:candidates.insert(0, configured)
        return list(dict.fromkeys(str(Path(p).resolve()) for p in candidates if p and Path(p).is_file()))

    def configure(self, executable, root):
        path, _ = validate_executable(executable)
        if Path(path).stem.lower() not in self.names:
            raise ValueError('Ejecutable no reconocido para '+self.key)
        folder = Path(root).expanduser()
        if not folder.is_absolute() or not folder.is_dir():
            raise ValueError('Selecciona una carpeta de ROMs existente con ruta absoluta.')
        self.store.set(self.key+'_executable', path)
        self.store.set('rom_root', str(folder.resolve()))

    def command(self, rom):
        executable = self.store.get(self.key+'_executable', '')
        path, _ = validate_executable(executable)
        target = Path(rom).resolve(strict=True)
        if not target.is_file() or target.suffix.lower() not in self.formats:
            raise ValueError('Formato o archivo de juego no válido.')
        return path, self.flags+[str(target)]

    def scan(self):
        root = Path(self.store.get('rom_root', ''))
        if not root.is_absolute() or not root.is_dir():raise ValueError('Configura primero la carpeta principal de ROMs.')
        added = 0
        self.result=dict(found=0,new=0,existing=0,errors=0)
        for platform in self.platforms:
            folder = root/platform
            if not folder.is_dir():continue
            for candidate in sorted(folder.rglob('*')):
                if candidate.is_symlink() or not candidate.is_file() or candidate.suffix.lower() not in self.formats:continue
                rom = candidate.resolve()
                if not rom.is_relative_to(folder.resolve()):continue
                self.result['found']+=1
                if self.store.db.execute(f'SELECT 1 FROM {self.table} WHERE path=?', (str(rom),)).fetchone():
                    self.result['existing']+=1;continue
                try:executable, args = self.command(rom)
                except (ValueError,OSError):self.result['errors']+=1;continue
                key = 'local-'+uuid.uuid4().hex
                with self.store.db:
                    # ROM identity is separate from executable identity: many games share Dolphin.
                    self.store.db.execute('INSERT INTO real_games(id,name,platform,executable,arguments,created_at) VALUES(?,?,?,?,?,?)', (key,rom.stem,platform,executable+'::'+key,json.dumps(args),utc_now()))
                    self.store.db.execute(f'INSERT INTO {self.table} VALUES(?,?)',(key,str(rom)))
                added += 1
                self.result['new']=added
        return added

    def resolve_game(self, game_id):
        row=self.store.db.execute(f'SELECT path FROM {self.table} WHERE game_id=?',(game_id,)).fetchone()
        return self.command(row[0]) if row else None
