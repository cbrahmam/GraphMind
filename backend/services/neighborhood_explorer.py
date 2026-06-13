from backend.neo4j_client import neo4j_client


def get_ego_graph(entity_name: str, radius: int = 2, limit: int = 100) -> dict:
    radius = min(radius, 4)

    center = neo4j_client.run_query(
        "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN n.name AS name, labels(n)[0] AS label LIMIT 1",
        {"name": entity_name},
    )
    if not center:
        return {"entity": entity_name, "found": False, "nodes": [], "links": []}

    actual_name = center[0]["name"]
    center_label = center[0]["label"]

    nodes_result = neo4j_client.run_query(
        "MATCH path = (n)-[*1.." + str(radius) + "]-(m) "
        "WHERE n.name = $name "
        "UNWIND nodes(path) AS node "
        "WITH DISTINCT node "
        "RETURN node.name AS name, labels(node)[0] AS label "
        "LIMIT $limit",
        {"name": actual_name, "limit": limit},
    )

    node_names = {n["name"] for n in nodes_result}
    node_names.add(actual_name)

    rels_result = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) "
        "WHERE a.name IN $names AND b.name IN $names "
        "RETURN DISTINCT a.name AS source, b.name AS target, type(r) AS type",
        {"names": list(node_names)},
    )

    layer_map = {actual_name: 0}
    for depth in range(1, radius + 1):
        neighbors = neo4j_client.run_query(
            "MATCH (n)-[*" + str(depth) + "]-(m) "
            "WHERE n.name = $name AND m.name IN $names "
            "RETURN DISTINCT m.name AS name",
            {"name": actual_name, "names": list(node_names - set(layer_map.keys()))},
        )
        for n in neighbors:
            if n["name"] not in layer_map:
                layer_map[n["name"]] = depth

    nodes = [
        {
            "name": n["name"],
            "label": n["label"],
            "layer": layer_map.get(n["name"], radius),
            "is_center": n["name"] == actual_name,
        }
        for n in nodes_result
    ]

    if not any(n["name"] == actual_name for n in nodes):
        nodes.insert(0, {"name": actual_name, "label": center_label, "layer": 0, "is_center": True})

    return {
        "entity": actual_name,
        "label": center_label,
        "found": True,
        "radius": radius,
        "node_count": len(nodes),
        "link_count": len(rels_result),
        "nodes": nodes,
        "links": [{"source": r["source"], "target": r["target"], "type": r["type"]} for r in rels_result],
        "layers": {str(d): len([n for n in nodes if n["layer"] == d]) for d in range(radius + 1)},
    }
