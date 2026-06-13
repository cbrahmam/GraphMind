import json
from datetime import datetime
from pathlib import Path
from backend.config import GRAPH_DATA_DIR

NOTIFICATIONS_FILE = Path(GRAPH_DATA_DIR) / "notifications.json"


def _load() -> list[dict]:
    if NOTIFICATIONS_FILE.exists():
        return json.loads(NOTIFICATIONS_FILE.read_text())
    return []


def _save(notifications: list[dict]):
    NOTIFICATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    NOTIFICATIONS_FILE.write_text(json.dumps(notifications, indent=2, default=str))


def create_notification(
    title: str,
    message: str,
    category: str = "info",
    source: str = "",
    entity: str = "",
) -> dict:
    notifications = _load()
    notif = {
        "id": f"notif_{len(notifications)+1}_{int(datetime.now().timestamp())}",
        "title": title,
        "message": message,
        "category": category,
        "source": source,
        "entity": entity,
        "created_at": datetime.now().isoformat(),
        "read": False,
    }
    notifications.insert(0, notif)
    if len(notifications) > 500:
        notifications = notifications[:500]
    _save(notifications)
    return notif


def get_notifications(
    limit: int = 50,
    unread_only: bool = False,
    category: str | None = None,
) -> list[dict]:
    notifications = _load()
    if unread_only:
        notifications = [n for n in notifications if not n.get("read")]
    if category:
        notifications = [n for n in notifications if n.get("category") == category]
    return notifications[:limit]


def mark_read(notification_id: str) -> bool:
    notifications = _load()
    for n in notifications:
        if n["id"] == notification_id:
            n["read"] = True
            _save(notifications)
            return True
    return False


def mark_all_read() -> int:
    notifications = _load()
    count = 0
    for n in notifications:
        if not n.get("read"):
            n["read"] = True
            count += 1
    _save(notifications)
    return count


def get_unread_count() -> int:
    return len([n for n in _load() if not n.get("read")])


def delete_notification(notification_id: str) -> bool:
    notifications = _load()
    before = len(notifications)
    notifications = [n for n in notifications if n["id"] != notification_id]
    _save(notifications)
    return len(notifications) < before


def clear_all() -> int:
    notifications = _load()
    count = len(notifications)
    _save([])
    return count
