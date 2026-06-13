import json
import shutil
from datetime import datetime
from pathlib import Path
from backend.config import GRAPH_DATA_DIR
from backend.neo4j_client import neo4j_client

BACKUPS_DIR = Path(GRAPH_DATA_DIR) / "backups"


def create_backup(name: str = "") -> dict:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = name or f"backup_{timestamp}"
    backup_dir = BACKUPS_DIR / backup_name
    backup_dir.mkdir(exist_ok=True)

    nodes = neo4j_client.run_query(
        "MATCH (n) RETURN n AS props, labels(n) AS labels, id(n) AS id"
    )
    rels = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) "
        "RETURN id(a) AS from_id, id(b) AS to_id, type(r) AS type, properties(r) AS props"
    )

    graph_data = {
        "nodes": [{"id": n["id"], "labels": n["labels"], "properties": dict(n["props"])} for n in nodes],
        "relationships": [{"from_id": r["from_id"], "to_id": r["to_id"], "type": r["type"],
                           "properties": dict(r["props"]) if r["props"] else {}} for r in rels],
    }

    (backup_dir / "graph.json").write_text(json.dumps(graph_data, indent=2, default=str))

    app_files = ["graphmind.db", "schema.json", "feeds.json", "webhooks.json",
                 "plugins.json", "notifications.json", "shared_views.json"]
    for f in app_files:
        src = Path(GRAPH_DATA_DIR) / f
        if src.exists():
            shutil.copy2(src, backup_dir / f)

    meta = {
        "name": backup_name,
        "created_at": datetime.now().isoformat(),
        "node_count": len(nodes),
        "relationship_count": len(rels),
        "files": [f.name for f in backup_dir.iterdir()],
    }
    (backup_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    return meta


def list_backups() -> list[dict]:
    if not BACKUPS_DIR.exists():
        return []

    backups = []
    for d in sorted(BACKUPS_DIR.iterdir(), reverse=True):
        if d.is_dir():
            meta_file = d / "meta.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text())
                backups.append(meta)
            else:
                backups.append({
                    "name": d.name,
                    "created_at": datetime.fromtimestamp(d.stat().st_mtime).isoformat(),
                })
    return backups


def restore_backup(backup_name: str) -> dict:
    backup_dir = BACKUPS_DIR / backup_name
    if not backup_dir.exists():
        return {"restored": False, "error": "Backup not found"}

    graph_file = backup_dir / "graph.json"
    if not graph_file.exists():
        return {"restored": False, "error": "No graph data in backup"}

    graph_data = json.loads(graph_file.read_text())

    neo4j_client.run_query("MATCH (n) DETACH DELETE n")

    id_map = {}
    for node in graph_data.get("nodes", []):
        labels = ":".join(node["labels"]) if node["labels"] else "Entity"
        props = node.get("properties", {})
        set_clauses = ", ".join(f"n.{k} = ${k}" for k in props.keys())
        result = neo4j_client.run_query(
            f"CREATE (n:{labels}) SET {set_clauses} RETURN id(n) AS new_id" if set_clauses
            else f"CREATE (n:{labels}) RETURN id(n) AS new_id",
            props,
        )
        if result:
            id_map[node["id"]] = result[0]["new_id"]

    rel_count = 0
    for rel in graph_data.get("relationships", []):
        from_new = id_map.get(rel["from_id"])
        to_new = id_map.get(rel["to_id"])
        if from_new is not None and to_new is not None:
            props = rel.get("properties", {})
            set_clause = " SET " + ", ".join(f"r.{k} = ${k}" for k in props.keys()) if props else ""
            neo4j_client.run_query(
                f"MATCH (a), (b) WHERE id(a) = $from_id AND id(b) = $to_id "
                f"CREATE (a)-[r:{rel['type']}]->(b){set_clause}",
                {"from_id": from_new, "to_id": to_new, **props},
            )
            rel_count += 1

    app_files = [f for f in backup_dir.iterdir() if f.name not in ("graph.json", "meta.json")]
    for f in app_files:
        shutil.copy2(f, Path(GRAPH_DATA_DIR) / f.name)

    return {
        "restored": True,
        "backup": backup_name,
        "nodes_restored": len(id_map),
        "relationships_restored": rel_count,
        "files_restored": [f.name for f in app_files],
    }


def delete_backup(backup_name: str) -> bool:
    backup_dir = BACKUPS_DIR / backup_name
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
        return True
    return False
