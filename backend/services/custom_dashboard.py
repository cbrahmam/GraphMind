import json
from datetime import datetime
from pathlib import Path
from backend.config import GRAPH_DATA_DIR

DASHBOARDS_FILE = Path(GRAPH_DATA_DIR) / "dashboards.json"


def _load() -> list[dict]:
    if DASHBOARDS_FILE.exists():
        return json.loads(DASHBOARDS_FILE.read_text())
    return []


def _save(dashboards: list[dict]):
    DASHBOARDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARDS_FILE.write_text(json.dumps(dashboards, indent=2, default=str))


WIDGET_TYPES = [
    "graph_stats", "entity_count", "relationship_count", "top_entities",
    "recent_activity", "label_distribution", "relationship_distribution",
    "health_score", "anomaly_summary", "query_box", "entity_search",
    "source_overview", "custom_cypher",
]


def create_dashboard(name: str, description: str = "", widgets: list[dict] | None = None) -> dict:
    dashboards = _load()
    dashboard = {
        "id": f"dash_{len(dashboards)+1}_{int(datetime.now().timestamp())}",
        "name": name,
        "description": description,
        "widgets": widgets or [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "layout": "grid",
    }
    dashboards.append(dashboard)
    _save(dashboards)
    return dashboard


def list_dashboards() -> list[dict]:
    return _load()


def get_dashboard(dashboard_id: str) -> dict | None:
    return next((d for d in _load() if d["id"] == dashboard_id), None)


def update_dashboard(dashboard_id: str, updates: dict) -> dict | None:
    dashboards = _load()
    for d in dashboards:
        if d["id"] == dashboard_id:
            for key in ["name", "description", "widgets", "layout"]:
                if key in updates:
                    d[key] = updates[key]
            d["updated_at"] = datetime.now().isoformat()
            _save(dashboards)
            return d
    return None


def delete_dashboard(dashboard_id: str) -> bool:
    dashboards = _load()
    before = len(dashboards)
    dashboards = [d for d in dashboards if d["id"] != dashboard_id]
    _save(dashboards)
    return len(dashboards) < before


def add_widget(dashboard_id: str, widget: dict) -> dict | None:
    dashboards = _load()
    for d in dashboards:
        if d["id"] == dashboard_id:
            widget_entry = {
                "id": f"w_{len(d['widgets'])+1}",
                "type": widget.get("type", "graph_stats"),
                "title": widget.get("title", ""),
                "config": widget.get("config", {}),
                "position": widget.get("position", {"x": 0, "y": 0, "w": 4, "h": 3}),
            }
            d["widgets"].append(widget_entry)
            d["updated_at"] = datetime.now().isoformat()
            _save(dashboards)
            return widget_entry
    return None


def remove_widget(dashboard_id: str, widget_id: str) -> bool:
    dashboards = _load()
    for d in dashboards:
        if d["id"] == dashboard_id:
            before = len(d["widgets"])
            d["widgets"] = [w for w in d["widgets"] if w["id"] != widget_id]
            if len(d["widgets"]) < before:
                d["updated_at"] = datetime.now().isoformat()
                _save(dashboards)
                return True
    return False


def get_available_widgets() -> list[dict]:
    return [
        {"type": wt, "description": wt.replace("_", " ").title()}
        for wt in WIDGET_TYPES
    ]
