from typing import Protocol
class InputSource(Protocol):
    """Future adapter emits logical actions: left/right/up/down/confirm/back."""
    def connected_devices(self) -> list[str]: ...
