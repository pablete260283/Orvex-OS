"""Explicit local metadata proposals. No simulated network search."""
import json


class LocalMetadata:
    def __init__(self, library):
        self.library = library
        self.pending = None

    def propose(self, game_id, value):
        self.pending = None
        data = json.loads(value)
        if not self.library.raw(game_id) or not isinstance(data, dict):
            raise ValueError('Juego o propuesta no válida')
        allowed = {'description', 'genre', 'year', 'edition', 'source'}
        if set(data) - allowed or any(not isinstance(v, (str, int)) for v in data.values()):
            raise ValueError('Campos no admitidos')
        self.pending = (game_id, data)
        return data

    def confirm(self):
        if self.pending is None:
            return
        game_id, data = self.pending
        with self.library.store.db:
            self.library.store.db.execute('UPDATE real_games SET metadata=? WHERE id=?', (json.dumps(data, ensure_ascii=False), game_id))
        self.pending = None
