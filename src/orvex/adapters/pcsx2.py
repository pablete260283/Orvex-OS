"""PCSX2 Qt direct boot; inherits non-mutating indexing and identity rules."""
from .dolphin import DolphinAdapter

class PCSX2Adapter(DolphinAdapter):
    key = 'pcsx2'
    table = 'pcsx2_roms'
    platforms = ['PS2']
    formats = {'.iso', '.bin', '.chd', '.cso', '.gz'}
    names = ['pcsx2', 'pcsx2-qt', 'pcsx2-qtx64', 'pcsx2-avx2', 'pcsx2-sse4']
    flags = ['-fullscreen', '-batch', '--']
