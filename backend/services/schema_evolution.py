import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.services.schema_manager import get_current_schema
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def suggest_schema_changes() -> dict:
    schema = get_current_schema()
    known_labels = {et["label"] for et in schema.get("entity_types", [])}
    known_rels = {rt["type"] for rt in schema.get("relationship_types", [])}

    actual_labels = neo4j_client.run_query(
        "CALL db.labels() YIELD label RETURN collect(label) AS labels"
    )
    actual_rels = neo4j_client.run_query(
        "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) AS types"
    )

    graph_labels = set(actual_labels[0]["labels"]) if actual_labels else set()
    graph_rels = set(actual_rels[0]["types"]) if actual_rels else set()

    new_labels = graph_labels - known_labels
    new_rels = graph_rels - known_rels

    sample_nodes = {}
    for label in new_labels:
        samples = neo4j_client.run_query(
            f"MATCH (n:{label}) RETURN n.name AS name, keys(n) AS props LIMIT 3"
        )
        sample_nodes[label] = [{"name": s["name"], "properties": s["props"]} for s in samples]

    sample_rels_data = {}
    for rel in new_rels:
        samples = neo4j_client.run_query(
            f"MATCH (a)-[r:{rel}]->(b) "
            "RETURN labels(a)[0] AS from_label, labels(b)[0] AS to_label LIMIT 3"
        )
        sample_rels_data[rel] = samples

    suggestions = []

    for label in new_labels:
        samples = sample_nodes.get(label, [])
        props = list(set(p for s in samples for p in s.get("properties", []) if not p.startswith("_") and p != "id"))
        suggestions.append({
            "type": "add_entity_type",
            "label": label,
            "description": f"Found {label} entities in graph not in current schema",
            "properties": props[:10],
            "sample_names": [s["name"] for s in samples],
        })

    for rel in new_rels:
        samples = sample_rels_data.get(rel, [])
        from_labels = list(set(s["from_label"] for s in samples if s.get("from_label")))
        to_labels = list(set(s["to_label"] for s in samples if s.get("to_label")))
        suggestions.append({
            "type": "add_relationship_type",
            "relationship": rel,
            "description": f"Found [{rel}] relationships not in current schema",
            "from_types": from_labels,
            "to_types": to_labels,
        })

    return {
        "current_schema_labels": sorted(known_labels),
        "current_schema_rels": sorted(known_rels),
        "graph_labels": sorted(graph_labels),
        "graph_rels": sorted(graph_rels),
        "suggestions": suggestions,
        "new_labels_count": len(new_labels),
        "new_rels_count": len(new_rels),
    }


def auto_evolve_schema() -> dict:
    suggestions = suggest_schema_changes()
    if not suggestions["suggestions"]:
        return {"evolved": False, "message": "Schema is up to date"}

    schema = get_current_schema()

    added_labels = 0
    added_rels = 0

    for s in suggestions["suggestions"]:
        if s["type"] == "add_entity_type":
            schema.setdefault("entity_types", []).append({
                "label": s["label"],
                "description": f"Auto-discovered from graph data",
                "properties": s.get("properties", []),
            })
            added_labels += 1
        elif s["type"] == "add_relationship_type":
            schema.setdefault("relationship_types", []).append({
                "type": s["relationship"],
                "description": f"Auto-discovered from graph data",
                "from_types": s.get("from_types", []),
                "to_types": s.get("to_types", []),
            })
            added_rels += 1

    from backend.services.schema_manager import save_schema
    save_schema(schema)

    return {
        "evolved": True,
        "added_labels": added_labels,
        "added_rels": added_rels,
        "suggestions_applied": len(suggestions["suggestions"]),
    }
