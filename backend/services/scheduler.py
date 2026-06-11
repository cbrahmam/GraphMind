import json
import uuid
import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from backend.config import GRAPH_DATA_DIR, UPLOAD_DIR

SCHEDULES_FILE = GRAPH_DATA_DIR / "schedules.json"
WATCH_DIR = UPLOAD_DIR / "watched"
WATCH_DIR.mkdir(exist_ok=True)

_running_tasks: dict[str, asyncio.Task] = {}


def _load_schedules() -> list[dict]:
    if SCHEDULES_FILE.exists():
        return json.loads(SCHEDULES_FILE.read_text())
    return []


def _save_schedules(schedules: list[dict]):
    SCHEDULES_FILE.write_text(json.dumps(schedules, indent=2))


def create_schedule(name: str, source_type: str, source_config: dict, interval_minutes: int = 60) -> dict:
    schedules = _load_schedules()
    schedule = {
        "id": str(uuid.uuid4()),
        "name": name,
        "source_type": source_type,
        "source_config": source_config,
        "interval_minutes": interval_minutes,
        "enabled": True,
        "last_run": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    schedules.append(schedule)
    _save_schedules(schedules)
    return schedule


def list_schedules() -> list[dict]:
    return _load_schedules()


def get_schedule(schedule_id: str) -> dict | None:
    for s in _load_schedules():
        if s["id"] == schedule_id:
            return s
    return None


def update_schedule(schedule_id: str, updates: dict) -> dict | None:
    schedules = _load_schedules()
    for s in schedules:
        if s["id"] == schedule_id:
            s.update(updates)
            _save_schedules(schedules)
            return s
    return None


def delete_schedule(schedule_id: str) -> bool:
    schedules = _load_schedules()
    before = len(schedules)
    schedules = [s for s in schedules if s["id"] != schedule_id]
    if len(schedules) < before:
        _save_schedules(schedules)
        return True
    return False


def check_watched_folder() -> list[str]:
    new_files = []
    processed_file = WATCH_DIR / ".processed"
    processed = set()
    if processed_file.exists():
        processed = set(processed_file.read_text().strip().split("\n"))

    for f in WATCH_DIR.iterdir():
        if f.name.startswith(".") or f.name in processed:
            continue
        if f.suffix.lower() in {".pdf", ".docx", ".txt", ".md", ".html", ".csv", ".json"}:
            new_files.append(str(f))

    return new_files


def mark_processed(filepath: str):
    processed_file = WATCH_DIR / ".processed"
    name = Path(filepath).name
    with open(processed_file, "a") as f:
        f.write(name + "\n")
