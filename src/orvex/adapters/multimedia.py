from typing import Protocol
class MediaPlayer(Protocol):
    """Future local/authorized media playback boundary."""
    def play(self, media_id: str) -> None: ...
