"""Progress-source boundary. No save-file inference or real integrations in this demo."""
import json
from pathlib import Path
from typing import Protocol
class ProgressProvider(Protocol):
    def get(self, profile: str, game_id: str) -> dict: ...
class DemoProgressProvider:
    def __init__(self):
        self.records=json.loads(Path(__file__).with_name("demo_progress.json").read_text())
    def get(self, profile, game_id):
        record=self.records.get(game_id)
        return dict(record,source="demo") if record else {}
def presentation(record):
    if not record:return {}
    percent=record.get("percent")
    minutes=record.get("minutes")
    return dict(record,percentLabel=(str(percent)+"%") if percent is not None else "Sin porcentaje disponible",timeLabel=(str(minutes//60)+" h "+str(minutes%60)+" min") if minutes is not None else "Tiempo no disponible",lastLabel=record.get("last_session") or "Sin sesiones",statusLabel={"not_started":"No iniciado","in_progress":"En progreso","completed":"Completado"}.get(record.get("status"),"Sin información"))
