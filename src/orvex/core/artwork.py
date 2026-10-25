"""Approved local artwork only. Metadata adapters must supply provenance separately.

This boundary never fetches remote images or treats API access as a copyright license.
"""
import json
from pathlib import Path
from typing import Protocol
ASSETS=Path(__file__).parents[1]/"ui/assets"
MANIFEST=Path(__file__).with_name("artwork.json")
class MetadataProvider(Protocol):
    def search(self, title: str) -> list[dict]: ...
    def artwork(self, provider_id: str) -> dict: ...
def resolve_art(key, role="cover", *, manifest=None, root=ASSETS):
    records=json.loads(MANIFEST.read_text()) if manifest is None else manifest
    record=records.get(key,{})
    if role not in ("cover","backdrop") or record.get("redistribution") is not True or not record.get("rights") or not record.get("source"):
        return ""
    candidate=(root/record.get(role,"")).resolve()
    if not candidate.is_relative_to(root.resolve()) or candidate.suffix.lower() not in (".svg",".png",".jpg",".jpeg",".webp") or not candidate.is_file():
        return ""
    return candidate.as_uri()
