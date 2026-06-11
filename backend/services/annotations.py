import json
import uuid
from datetime import datetime, timezone
from backend.config import GRAPH_DATA_DIR

ANNOTATIONS_FILE = GRAPH_DATA_DIR / "annotations.json"


def _load() -> list[dict]:
    if ANNOTATIONS_FILE.exists():
        return json.loads(ANNOTATIONS_FILE.read_text())
    return []


def _save(annotations: list[dict]):
    ANNOTATIONS_FILE.write_text(json.dumps(annotations, indent=2))


def add_annotation(entity_name: str, text: str, annotation_type: str = "note", user: str = "anonymous") -> dict:
    annotations = _load()
    annotation = {
        "id": str(uuid.uuid4()),
        "entity_name": entity_name,
        "text": text,
        "type": annotation_type,
        "user": user,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "votes": 0,
    }
    annotations.append(annotation)
    _save(annotations)
    return annotation


def get_annotations(entity_name: str | None = None) -> list[dict]:
    annotations = _load()
    if entity_name:
        return [a for a in annotations if a["entity_name"] == entity_name]
    return annotations


def vote_annotation(annotation_id: str, direction: int) -> dict | None:
    annotations = _load()
    for a in annotations:
        if a["id"] == annotation_id:
            a["votes"] += direction
            _save(annotations)
            return a
    return None


def delete_annotation(annotation_id: str) -> bool:
    annotations = _load()
    before = len(annotations)
    annotations = [a for a in annotations if a["id"] != annotation_id]
    if len(annotations) < before:
        _save(annotations)
        return True
    return False


def flag_entity(entity_name: str, reason: str, user: str = "anonymous") -> dict:
    return add_annotation(entity_name, reason, annotation_type="flag", user=user)


def correct_entity(entity_name: str, field: str, old_value: str, new_value: str, user: str = "anonymous") -> dict:
    text = f"Correction: {field} changed from '{old_value}' to '{new_value}'"
    return add_annotation(entity_name, text, annotation_type="correction", user=user)
