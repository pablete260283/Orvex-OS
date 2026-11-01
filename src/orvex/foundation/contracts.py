"""Typed integration boundaries; no network, player or PIN implementation is pretended."""

from dataclasses import dataclass
from typing import Protocol, Iterable, Mapping
from .models import Content


@dataclass(frozen=True)
class LaunchPlan:
    content_id: str
    executable: str
    arguments: tuple[str, ...]
    engine: str
    confirmation_required: bool = True


@dataclass(frozen=True)
class MetadataCandidate:
    provider: str
    provider_id: str
    title: str
    platform: str
    edition: str
    fields: Mapping
    attribution: str
    artwork_license: str | None = None


class MetadataProvider(Protocol):
    def search(self, title: str, platform: str) -> Iterable[MetadataCandidate]: ...


class ArtworkProvider(Protocol):
    def fetch_authorized(self, candidate: MetadataCandidate, destination: str) -> str:
        """Require authorization/license and do not overwrite an approved asset."""
        ...


class MultimediaPlayer(Protocol):
    def supports(self, content: Content) -> bool: ...
    def prepare(self, content: Content, profile_id: str) -> object: ...
    def play(self, prepared: object, confirmed: bool) -> object: ...
    def request_stop(self, session: object) -> bool: ...


class ExternalApplicationLauncher(Protocol):
    def prepare(self, content: Content, profile_id: str) -> LaunchPlan: ...
    def launch(self, plan: LaunchPlan, confirmed: bool) -> object: ...


class LegacyGameGateway:
    """Functional boundary to the existing confirmed GameLauncher, not a replacement."""

    def __init__(self, catalog, launcher):
        self.catalog = catalog
        self.launcher = launcher

    def request(self, content_id, profile_id):
        content = self.catalog.get(content_id, profile_id)
        if not content.legacy_game:
            raise ValueError("Este contenido aún no tiene un lanzador integrado.")
        self.launcher.request(content_id)
