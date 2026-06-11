import json
import uuid
from datetime import datetime, timezone
from backend.config import GRAPH_DATA_DIR

WORKSPACES_FILE = GRAPH_DATA_DIR / "workspaces.json"

_active_workspace: str | None = None


def _load() -> list[dict]:
    if WORKSPACES_FILE.exists():
        return json.loads(WORKSPACES_FILE.read_text())
    return [{"id": "default", "name": "Default", "description": "Default workspace", "created_at": "", "neo4j_database": "neo4j"}]


def _save(workspaces: list[dict]):
    WORKSPACES_FILE.write_text(json.dumps(workspaces, indent=2))


def create_workspace(name: str, description: str = "") -> dict:
    workspaces = _load()
    ws = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "neo4j_database": f"ws_{name.lower().replace(' ', '_')}",
    }
    workspaces.append(ws)
    _save(workspaces)
    return ws


def list_workspaces() -> list[dict]:
    return _load()


def get_workspace(ws_id: str) -> dict | None:
    for ws in _load():
        if ws["id"] == ws_id:
            return ws
    return None


def delete_workspace(ws_id: str) -> bool:
    if ws_id == "default":
        return False
    workspaces = _load()
    before = len(workspaces)
    workspaces = [w for w in workspaces if w["id"] != ws_id]
    if len(workspaces) < before:
        _save(workspaces)
        return True
    return False


def get_active_workspace() -> str:
    global _active_workspace
    return _active_workspace or "default"


def set_active_workspace(ws_id: str) -> bool:
    global _active_workspace
    ws = get_workspace(ws_id)
    if ws:
        _active_workspace = ws_id
        return True
    return False
