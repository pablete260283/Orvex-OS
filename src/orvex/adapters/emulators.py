from typing import Protocol
class GameLauncher(Protocol):
    """Future adapter: resolves platform/configuration; never exposed as an emulator picker."""
    def launch(self, game_id: str) -> None: ...
