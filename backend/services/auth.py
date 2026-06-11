import json
import uuid
import hashlib
import secrets
from datetime import datetime, timezone
from backend.config import GRAPH_DATA_DIR

USERS_FILE = GRAPH_DATA_DIR / "users.json"
TOKENS_FILE = GRAPH_DATA_DIR / "tokens.json"


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt).encode()).hexdigest()


def _load_users() -> list[dict]:
    if USERS_FILE.exists():
        return json.loads(USERS_FILE.read_text())
    return []


def _save_users(users: list[dict]):
    USERS_FILE.write_text(json.dumps(users, indent=2))


def _load_tokens() -> dict:
    if TOKENS_FILE.exists():
        return json.loads(TOKENS_FILE.read_text())
    return {}


def _save_tokens(tokens: dict):
    TOKENS_FILE.write_text(json.dumps(tokens, indent=2))


def create_user(username: str, password: str, role: str = "viewer") -> dict:
    users = _load_users()
    if any(u["username"] == username for u in users):
        raise ValueError(f"User '{username}' already exists")

    salt = secrets.token_hex(16)
    user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password_hash": _hash_password(password, salt),
        "salt": salt,
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    users.append(user)
    _save_users(users)
    return {"id": user["id"], "username": username, "role": role}


def authenticate(username: str, password: str) -> dict | None:
    users = _load_users()
    for u in users:
        if u["username"] == username:
            if _hash_password(password, u["salt"]) == u["password_hash"]:
                token = secrets.token_urlsafe(32)
                tokens = _load_tokens()
                tokens[token] = {
                    "user_id": u["id"],
                    "username": u["username"],
                    "role": u["role"],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                _save_tokens(tokens)
                return {"token": token, "user_id": u["id"], "username": username, "role": u["role"]}
            return None
    return None


def validate_token(token: str) -> dict | None:
    tokens = _load_tokens()
    return tokens.get(token)


def revoke_token(token: str) -> bool:
    tokens = _load_tokens()
    if token in tokens:
        del tokens[token]
        _save_tokens(tokens)
        return True
    return False


def list_users() -> list[dict]:
    users = _load_users()
    return [{"id": u["id"], "username": u["username"], "role": u["role"]} for u in users]


def check_permission(token: str, required_role: str) -> bool:
    user = validate_token(token)
    if not user:
        return False
    role_hierarchy = {"admin": 3, "editor": 2, "viewer": 1}
    return role_hierarchy.get(user["role"], 0) >= role_hierarchy.get(required_role, 0)
