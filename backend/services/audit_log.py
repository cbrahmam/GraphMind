import json
from datetime import datetime
from pathlib import Path
from backend.config import GRAPH_DATA_DIR

AUDIT_FILE = Path(GRAPH_DATA_DIR) / "audit_log.jsonl"


def log_event(
    action: str,
    resource: str,
    user: str = "anonymous",
    details: dict | None = None,
    ip_address: str = "",
) -> dict:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "resource": resource,
        "user": user,
        "details": details or {},
        "ip_address": ip_address,
    }

    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_FILE, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")

    return entry


def get_logs(
    limit: int = 100,
    action: str | None = None,
    user: str | None = None,
    resource: str | None = None,
    since: str | None = None,
) -> list[dict]:
    if not AUDIT_FILE.exists():
        return []

    logs = []
    with open(AUDIT_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    logs.append(entry)
                except json.JSONDecodeError:
                    continue

    if action:
        logs = [l for l in logs if l.get("action") == action]
    if user:
        logs = [l for l in logs if l.get("user") == user]
    if resource:
        logs = [l for l in logs if resource in l.get("resource", "")]
    if since:
        logs = [l for l in logs if l.get("timestamp", "") >= since]

    logs.reverse()
    return logs[:limit]


def get_log_stats() -> dict:
    logs = get_logs(limit=10000)

    actions = {}
    users = {}
    resources = {}
    for log in logs:
        a = log.get("action", "unknown")
        u = log.get("user", "unknown")
        r = log.get("resource", "unknown")
        actions[a] = actions.get(a, 0) + 1
        users[u] = users.get(u, 0) + 1
        resources[r] = resources.get(r, 0) + 1

    return {
        "total_events": len(logs),
        "actions": dict(sorted(actions.items(), key=lambda x: -x[1])),
        "users": dict(sorted(users.items(), key=lambda x: -x[1])),
        "top_resources": dict(sorted(resources.items(), key=lambda x: -x[1])[:20]),
    }


def clear_logs() -> dict:
    if AUDIT_FILE.exists():
        count = sum(1 for _ in open(AUDIT_FILE))
        AUDIT_FILE.write_text("")
        return {"cleared": True, "entries_removed": count}
    return {"cleared": True, "entries_removed": 0}
