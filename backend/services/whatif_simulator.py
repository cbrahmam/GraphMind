from backend.neo4j_client import neo4j_client


def simulate_remove_entity(entity_name: str) -> dict:
    node = neo4j_client.run_query(
        "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN n.name AS name, labels(n)[0] AS label LIMIT 1",
        {"name": entity_name},
    )
    if not node:
        return {"entity": entity_name, "found": False}

    actual_name = node[0]["name"]

    rels = neo4j_client.run_query(
        "MATCH (n)-[r]-(m) WHERE n.name = $name "
        "RETURN type(r) AS type, m.name AS related, labels(m)[0] AS label",
        {"name": actual_name},
    )

    would_disconnect = neo4j_client.run_query(
        "MATCH (n)-[]-(m) WHERE n.name = $name "
        "WITH collect(DISTINCT m) AS neighbors "
        "UNWIND neighbors AS a "
        "UNWIND neighbors AS b "
        "WHERE id(a) < id(b) "
        "OPTIONAL MATCH path = shortestPath((a)-[*1..5]-(b)) "
        "WHERE NONE(node IN nodes(path) WHERE node.name = $name) "
        "WITH a, b, path "
        "WHERE path IS NULL "
        "RETURN a.name AS entity_a, b.name AS entity_b "
        "LIMIT 20",
        {"name": actual_name},
    )

    orphaned = neo4j_client.run_query(
        "MATCH (n)-[]-(m) WHERE n.name = $name "
        "WITH m "
        "MATCH (m)-[r]-() "
        "WITH m, count(r) AS degree "
        "WHERE degree = 1 "
        "RETURN m.name AS name, labels(m)[0] AS label",
        {"name": actual_name},
    )

    return {
        "entity": actual_name,
        "label": node[0]["label"],
        "found": True,
        "relationships_removed": len(rels),
        "affected_entities": [{"name": r["related"], "label": r["label"], "via": r["type"]} for r in rels],
        "would_orphan": [{"name": o["name"], "label": o["label"]} for o in orphaned],
        "would_disconnect_pairs": [{"a": d["entity_a"], "b": d["entity_b"]} for d in would_disconnect],
        "impact_score": len(rels) + len(orphaned) * 2 + len(would_disconnect) * 3,
    }


def simulate_add_relationship(from_entity: str, to_entity: str, rel_type: str) -> dict:
    from_node = neo4j_client.run_query(
        "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN n.name AS name, labels(n)[0] AS label LIMIT 1",
        {"name": from_entity},
    )
    to_node = neo4j_client.run_query(
        "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN n.name AS name, labels(n)[0] AS label LIMIT 1",
        {"name": to_entity},
    )

    if not from_node or not to_node:
        return {"error": "One or both entities not found"}

    existing_path = neo4j_client.run_query(
        "MATCH path = shortestPath((a)-[*1..6]-(b)) "
        "WHERE a.name = $from AND b.name = $to "
        "RETURN length(path) AS distance",
        {"from": from_node[0]["name"], "to": to_node[0]["name"]},
    )

    current_distance = existing_path[0]["distance"] if existing_path else -1

    from_neighbors = neo4j_client.run_query(
        "MATCH (n)-[]-(m) WHERE n.name = $name RETURN collect(DISTINCT m.name) AS names",
        {"name": from_node[0]["name"]},
    )
    to_neighbors = neo4j_client.run_query(
        "MATCH (n)-[]-(m) WHERE n.name = $name RETURN collect(DISTINCT m.name) AS names",
        {"name": to_node[0]["name"]},
    )

    from_set = set(from_neighbors[0]["names"]) if from_neighbors else set()
    to_set = set(to_neighbors[0]["names"]) if to_neighbors else set()
    newly_reachable = to_set - from_set

    return {
        "from": from_node[0]["name"],
        "to": to_node[0]["name"],
        "relationship": rel_type,
        "current_distance": current_distance,
        "new_distance": 1,
        "distance_reduction": max(0, current_distance - 1) if current_distance > 0 else 0,
        "currently_connected": current_distance > 0,
        "newly_reachable_from_source": sorted(list(newly_reachable))[:15],
        "impact": "high" if current_distance < 0 else "medium" if current_distance > 3 else "low",
    }
