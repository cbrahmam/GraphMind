import json
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from backend.config import GRAPH_DATA_DIR

KEYS_FILE = Path(GRAPH_DATA_DIR) / "api_keys.json"


def _load() -> list[dict]:
    if KEYS_FILE.exists():
        return json.loads(KEYS_FILE.read_text())
    return []


def _save(keys: list[dict]):
    KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEYS_FILE.write_text(json.dumps(keys, indent=2, default=str))


def generate_key(
    name: str,
    scopes: list[str] | None = None,
    rate_limit: int = 60,
    owner: str = "anonymous",
) -> dict:
    raw_key = f"gm_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    keys = _load()
    entry = {
        "id": f"key_{len(keys)+1}",
        "name": name,
        "key_hash": key_hash,
        "key_prefix": raw_key[:8],
        "scopes": scopes or ["read"],
        "rate_limit_per_minute": rate_limit,
        "owner": owner,
        "active": True,
        "created_at": datetime.now().isoformat(),
        "last_used": None,
        "usage_count": 0,
    }
    keys.append(entry)
    _save(keys)

    return {
        "id": entry["id"],
        "name": name,
        "api_key": raw_key,
        "key_prefix": entry["key_prefix"],
        "scopes": entry["scopes"],
        "rate_limit_per_minute": rate_limit,
        "message": "Save this key — it won't be shown again",
    }


def validate_key(raw_key: str) -> dict | None:
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    keys = _load()

    for k in keys:
        if k["key_hash"] == key_hash and k.get("active"):
            k["last_used"] = datetime.now().isoformat()
            k["usage_count"] = k.get("usage_count", 0) + 1
            _save(keys)
            return {
                "id": k["id"],
                "name": k["name"],
                "scopes": k["scopes"],
                "rate_limit_per_minute": k["rate_limit_per_minute"],
                "owner": k["owner"],
            }
    return None


def list_keys() -> list[dict]:
    return [
        {k: v for k, v in key.items() if k != "key_hash"}
        for key in _load()
    ]


def revoke_key(key_id: str) -> bool:
    keys = _load()
    for k in keys:
        if k["id"] == key_id:
            k["active"] = False
            k["revoked_at"] = datetime.now().isoformat()
            _save(keys)
            return True
    return False


def delete_key(key_id: str) -> bool:
    keys = _load()
    before = len(keys)
    keys = [k for k in keys if k["id"] != key_id]
    _save(keys)
    return len(keys) < before


def get_key_stats() -> dict:
    keys = _load()
    return {
        "total_keys": len(keys),
        "active_keys": len([k for k in keys if k.get("active")]),
        "revoked_keys": len([k for k in keys if not k.get("active")]),
        "total_usage": sum(k.get("usage_count", 0) for k in keys),
    }
