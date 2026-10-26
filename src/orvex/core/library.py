"""Deterministic demo-catalog queries, independent of Qt and hardware adapters."""

import unicodedata
import math
from .store import catalog

PROFILES = ("adult", "child")


def normalized(value):
    return "".join(
        c for c in unicodedata.normalize("NFD", value.casefold()) if unicodedata.category(c) != "Mn"
    )


class LibraryService:
    def __init__(self, store, items=None):
        self.store = store
        self.items = catalog() if items is None else items

    def allowed(self, entry, profile):
        if not isinstance(entry, dict) or profile not in PROFILES:
            return False
        if profile == "adult":
            return True
        age = entry.get("age")
        return (
            isinstance(age, (int, float))
            and not isinstance(age, bool)
            and 0 <= age <= 7
            and math.isfinite(age)
            and age == int(age)
        )

    def visible(self, profile, kind=None):
        return [
            e
            for e in self.items
            if self.allowed(e, profile) and (kind is None or e["kind"] == kind)
        ]

    def options(self, profile, kind):
        field = "platform" if kind == "game" else "media_type"
        return ["Todas"] + sorted({e[field] for e in self.visible(profile, kind)})

    def query(self, profile, kind=None, query="", category="Todas", favorites_only=False):
        favorites = set(self.store.favorites(profile))
        field = "platform" if kind == "game" else "media_type"
        return [
            dict(e, favorite=e["id"] in favorites)
            for e in self.visible(profile, kind)
            if normalized(query.strip()) in normalized(e["title"])
            and (category == "Todas" or e.get(field) == category)
            and (not favorites_only or e["id"] in favorites)
        ]

    def lookup(self, item_id, profile):
        return next(
            (
                dict(e, favorite=e["id"] in self.store.favorites(profile))
                for e in self.visible(profile)
                if e["id"] == item_id
            ),
            {},
        )

    def toggle_favorite(self, item_id, profile):
        if not self.lookup(item_id, profile):
            return False
        self.store.set_favorite(profile, item_id, item_id not in self.store.favorites(profile))
        return True
