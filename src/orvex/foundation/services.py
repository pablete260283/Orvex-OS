"""Composition root shared by Qt and the offline command line."""

from .repository import SQLiteRepository
from .profiles import ProfileService
from .catalog import CatalogService
from .contracts import LegacyGameGateway


class FoundationServices:
    def __init__(self, store, launcher=None, authorizer=None):
        self.repository = SQLiteRepository(store)
        self.profiles = ProfileService(self.repository, authorizer)
        self.catalog = CatalogService(self.repository, self.profiles)
        self.games = LegacyGameGateway(self.catalog, launcher) if launcher is not None else None
