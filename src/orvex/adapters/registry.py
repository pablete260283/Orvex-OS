"""Only registered adapters resolve indexed games; native games remain unchanged."""
from .dolphin import DolphinAdapter
from .pcsx2 import PCSX2Adapter

ADAPTERS = {'dolphin': DolphinAdapter, 'pcsx2': PCSX2Adapter}

def resolve(store, game_id):
    for adapter in ADAPTERS.values():
        command = adapter(store).resolve_game(game_id)
        if command:return command
    return None
