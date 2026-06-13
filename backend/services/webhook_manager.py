import json
import httpx
from datetime import datetime
from pathlib import Path
from backend.config import GRAPH_DATA_DIR

WEBHOOKS_FILE = Path(GRAPH_DATA_DIR) / "webhooks.json"


def _load() -> list[dict]:
    if WEBHOOKS_FILE.exists():
        return json.loads(WEBHOOKS_FILE.read_text())
    return []


def _save(webhooks: list[dict]):
    WEBHOOKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    WEBHOOKS_FILE.write_text(json.dumps(webhooks, indent=2, default=str))


def register_webhook(url: str, events: list[str], name: str = "", secret: str = "") -> dict:
    webhooks = _load()
    webhook = {
        "id": f"wh_{len(webhooks)+1}_{int(datetime.now().timestamp())}",
        "url": url,
        "events": events,
        "name": name or url,
        "secret": secret,
        "active": True,
        "created_at": datetime.now().isoformat(),
        "last_triggered": None,
        "trigger_count": 0,
        "last_status": None,
    }
    webhooks.append(webhook)
    _save(webhooks)
    return webhook


def list_webhooks() -> list[dict]:
    return [{k: v for k, v in w.items() if k != "secret"} for w in _load()]


def delete_webhook(webhook_id: str) -> bool:
    webhooks = _load()
    before = len(webhooks)
    webhooks = [w for w in webhooks if w["id"] != webhook_id]
    _save(webhooks)
    return len(webhooks) < before


def toggle_webhook(webhook_id: str) -> dict | None:
    webhooks = _load()
    for w in webhooks:
        if w["id"] == webhook_id:
            w["active"] = not w["active"]
            _save(webhooks)
            return w
    return None


def fire_webhooks(event: str, payload: dict):
    webhooks = _load()
    results = []

    for w in webhooks:
        if not w.get("active"):
            continue
        if event not in w.get("events", []) and "*" not in w.get("events", []):
            continue

        body = {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "payload": payload,
        }

        headers = {"Content-Type": "application/json"}
        if w.get("secret"):
            headers["X-Webhook-Secret"] = w["secret"]

        try:
            resp = httpx.post(w["url"], json=body, headers=headers, timeout=10)
            w["last_triggered"] = datetime.now().isoformat()
            w["trigger_count"] = w.get("trigger_count", 0) + 1
            w["last_status"] = resp.status_code
            results.append({"webhook_id": w["id"], "status": resp.status_code, "success": resp.status_code < 400})
        except Exception as e:
            w["last_status"] = "error"
            results.append({"webhook_id": w["id"], "status": "error", "error": str(e)})

    _save(webhooks)
    return results


def test_webhook(webhook_id: str) -> dict:
    webhooks = _load()
    webhook = next((w for w in webhooks if w["id"] == webhook_id), None)
    if not webhook:
        return {"error": "Webhook not found"}

    try:
        resp = httpx.post(
            webhook["url"],
            json={"event": "test", "timestamp": datetime.now().isoformat(), "payload": {"test": True}},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        return {"status": resp.status_code, "success": resp.status_code < 400, "body": resp.text[:500]}
    except Exception as e:
        return {"status": "error", "success": False, "error": str(e)}
