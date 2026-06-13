import json
import re
from datetime import datetime
from pathlib import Path
from backend.config import GRAPH_DATA_DIR

PLUGINS_FILE = Path(GRAPH_DATA_DIR) / "plugins.json"


def _load() -> list[dict]:
    if PLUGINS_FILE.exists():
        return json.loads(PLUGINS_FILE.read_text())
    return []


def _save(plugins: list[dict]):
    PLUGINS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PLUGINS_FILE.write_text(json.dumps(plugins, indent=2, default=str))


def create_plugin(
    name: str,
    description: str,
    rules: list[dict],
    entity_label: str = "Entity",
) -> dict:
    plugins = _load()
    plugin = {
        "id": f"plugin_{len(plugins)+1}",
        "name": name,
        "description": description,
        "entity_label": entity_label,
        "rules": rules,
        "active": True,
        "created_at": datetime.now().isoformat(),
        "match_count": 0,
    }
    plugins.append(plugin)
    _save(plugins)
    return plugin


def list_plugins() -> list[dict]:
    return _load()


def get_plugin(plugin_id: str) -> dict | None:
    plugins = _load()
    return next((p for p in plugins if p["id"] == plugin_id), None)


def delete_plugin(plugin_id: str) -> bool:
    plugins = _load()
    before = len(plugins)
    plugins = [p for p in plugins if p["id"] != plugin_id]
    _save(plugins)
    return len(plugins) < before


def toggle_plugin(plugin_id: str) -> dict | None:
    plugins = _load()
    for p in plugins:
        if p["id"] == plugin_id:
            p["active"] = not p["active"]
            _save(plugins)
            return p
    return None


def run_plugin(plugin_id: str, text: str) -> dict:
    plugin = get_plugin(plugin_id)
    if not plugin:
        return {"error": "Plugin not found"}
    if not plugin.get("active"):
        return {"error": "Plugin is disabled"}

    entities = []
    for rule in plugin.get("rules", []):
        rule_type = rule.get("type", "regex")
        pattern = rule.get("pattern", "")

        if rule_type == "regex" and pattern:
            try:
                matches = re.finditer(pattern, text)
                for m in matches:
                    name = m.group(1) if m.lastindex and m.lastindex >= 1 else m.group(0)
                    entities.append({
                        "name": name,
                        "label": rule.get("label", plugin.get("entity_label", "Entity")),
                        "matched_by": pattern,
                        "properties": rule.get("properties", {}),
                    })
            except re.error:
                continue

        elif rule_type == "keyword" and pattern:
            keywords = [k.strip() for k in pattern.split(",")]
            for kw in keywords:
                if kw.lower() in text.lower():
                    start = text.lower().index(kw.lower())
                    entities.append({
                        "name": text[start:start + len(kw)],
                        "label": rule.get("label", plugin.get("entity_label", "Entity")),
                        "matched_by": f"keyword:{kw}",
                    })

        elif rule_type == "template" and pattern:
            template_re = pattern.replace("{entity}", "(.+?)")
            try:
                matches = re.finditer(template_re, text)
                for m in matches:
                    entities.append({
                        "name": m.group(1),
                        "label": rule.get("label", plugin.get("entity_label", "Entity")),
                        "matched_by": f"template:{pattern}",
                    })
            except re.error:
                continue

    plugins = _load()
    for p in plugins:
        if p["id"] == plugin_id:
            p["match_count"] = p.get("match_count", 0) + len(entities)
    _save(plugins)

    return {
        "plugin": plugin["name"],
        "entities_found": len(entities),
        "entities": entities,
    }


def run_all_plugins(text: str) -> dict:
    plugins = _load()
    all_entities = []

    for p in plugins:
        if p.get("active"):
            result = run_plugin(p["id"], text)
            all_entities.extend(result.get("entities", []))

    return {
        "plugins_run": len([p for p in plugins if p.get("active")]),
        "total_entities": len(all_entities),
        "entities": all_entities,
    }
