import json
import uuid
from datetime import datetime, timezone
from backend.config import GRAPH_DATA_DIR
from backend.neo4j_client import neo4j_client

WATCHLIST_FILE = GRAPH_DATA_DIR / "watchlist.json"
ALERTS_FILE = GRAPH_DATA_DIR / "watchlist_alerts.json"


def _load_watchlist() -> list[dict]:
    if WATCHLIST_FILE.exists():
        return json.loads(WATCHLIST_FILE.read_text())
    return []


def _save_watchlist(items: list[dict]):
    WATCHLIST_FILE.write_text(json.dumps(items, indent=2))


def _load_alerts() -> list[dict]:
    if ALERTS_FILE.exists():
        return json.loads(ALERTS_FILE.read_text())
    return []


def _save_alerts(alerts: list[dict]):
    ALERTS_FILE.write_text(json.dumps(alerts, indent=2))


def add_watch(entity_pattern: str, label: str | None = None, notify: str = "log") -> dict:
    items = _load_watchlist()
    item = {
        "id": str(uuid.uuid4()),
        "pattern": entity_pattern,
        "label": label,
        "notify": notify,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "enabled": True,
    }
    items.append(item)
    _save_watchlist(items)
    return item


def list_watches() -> list[dict]:
    return _load_watchlist()


def remove_watch(watch_id: str) -> bool:
    items = _load_watchlist()
    before = len(items)
    items = [i for i in items if i["id"] != watch_id]
    if len(items) < before:
        _save_watchlist(items)
        return True
    return False


def check_new_entities(entity_names: list[str]) -> list[dict]:
    watches = _load_watchlist()
    if not watches:
        return []

    alerts = []
    for name in entity_names:
        for watch in watches:
            if not watch.get("enabled"):
                continue
            if watch["pattern"].lower() in name.lower():
                alert = {
                    "id": str(uuid.uuid4()),
                    "watch_id": watch["id"],
                    "entity_name": name,
                    "pattern": watch["pattern"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "read": False,
                }
                alerts.append(alert)

    if alerts:
        existing = _load_alerts()
        existing.extend(alerts)
        _save_alerts(existing[-500:])

    return alerts


def get_alerts(unread_only: bool = False) -> list[dict]:
    alerts = _load_alerts()
    if unread_only:
        return [a for a in alerts if not a.get("read")]
    return alerts


def mark_alert_read(alert_id: str) -> bool:
    alerts = _load_alerts()
    for a in alerts:
        if a["id"] == alert_id:
            a["read"] = True
            _save_alerts(alerts)
            return True
    return False
