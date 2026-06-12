import json
import hashlib
from datetime import datetime
from pathlib import Path
from backend.config import GRAPH_DATA_DIR

VIEWS_FILE = Path(GRAPH_DATA_DIR) / "shared_views.json"


def _load_views() -> list[dict]:
    if VIEWS_FILE.exists():
        return json.loads(VIEWS_FILE.read_text())
    return []


def _save_views(views: list[dict]):
    VIEWS_FILE.parent.mkdir(parents=True, exist_ok=True)
    VIEWS_FILE.write_text(json.dumps(views, indent=2, default=str))


def create_shared_view(
    name: str,
    description: str,
    query: str,
    filters: dict | None = None,
    layout: dict | None = None,
    created_by: str = "anonymous",
) -> dict:
    views = _load_views()
    view_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:12]

    view = {
        "id": view_id,
        "name": name,
        "description": description,
        "query": query,
        "filters": filters or {},
        "layout": layout or {},
        "created_by": created_by,
        "created_at": datetime.now().isoformat(),
        "view_count": 0,
        "is_public": True,
    }
    views.append(view)
    _save_views(views)
    return view


def get_shared_view(view_id: str) -> dict | None:
    views = _load_views()
    for v in views:
        if v["id"] == view_id:
            v["view_count"] = v.get("view_count", 0) + 1
            _save_views(views)
            return v
    return None


def list_shared_views() -> list[dict]:
    return _load_views()


def delete_shared_view(view_id: str) -> bool:
    views = _load_views()
    before = len(views)
    views = [v for v in views if v["id"] != view_id]
    _save_views(views)
    return len(views) < before


def update_shared_view(view_id: str, updates: dict) -> dict | None:
    views = _load_views()
    for v in views:
        if v["id"] == view_id:
            for key in ["name", "description", "query", "filters", "layout", "is_public"]:
                if key in updates:
                    v[key] = updates[key]
            v["updated_at"] = datetime.now().isoformat()
            _save_views(views)
            return v
    return None
