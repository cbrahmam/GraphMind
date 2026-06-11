import json
from datetime import datetime, timezone
from backend.config import GRAPH_DATA_DIR

FEED_FILE = GRAPH_DATA_DIR / "change_feed.jsonl"


def record_change(change_type: str, details: dict):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": change_type,
        **details,
    }
    with open(FEED_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def record_node_created(name: str, label: str, source: str):
    record_change("node_created", {"name": name, "label": label, "source": source})


def record_node_updated(name: str, label: str, fields: list[str]):
    record_change("node_updated", {"name": name, "label": label, "fields_updated": fields})


def record_relationship_created(from_name: str, rel_type: str, to_name: str, source: str):
    record_change("relationship_created", {
        "from": from_name, "type": rel_type, "to": to_name, "source": source,
    })


def record_extraction(document: str, entities: int, relationships: int):
    record_change("extraction_complete", {
        "document": document, "entities": entities, "relationships": relationships,
    })


def record_graph_clear():
    record_change("graph_cleared", {})


def get_feed(limit: int = 100, change_type: str | None = None) -> list[dict]:
    if not FEED_FILE.exists():
        return []
    entries = []
    with open(FEED_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if change_type and entry.get("type") != change_type:
                    continue
                entries.append(entry)
            except json.JSONDecodeError:
                continue
    entries.reverse()
    return entries[:limit]


def get_timeline() -> list[dict]:
    feed = get_feed(limit=500, change_type="extraction_complete")
    timeline = []
    for entry in reversed(feed):
        timeline.append({
            "timestamp": entry["timestamp"],
            "document": entry.get("document", ""),
            "entities": entry.get("entities", 0),
            "relationships": entry.get("relationships", 0),
        })
    return timeline
