from backend.neo4j_client import neo4j_client


def find_shortest_path(from_entity: str, to_entity: str, max_depth: int = 10) -> dict:
    paths = neo4j_client.run_query(
        "MATCH path = shortestPath((a)-[*1.." + str(min(max_depth, 15)) + "]-(b)) "
        "WHERE toLower(a.name) CONTAINS toLower($from) "
        "AND toLower(b.name) CONTAINS toLower($to) "
        "RETURN [n IN nodes(path) | {name: n.name, label: labels(n)[0]}] AS nodes, "
        "[r IN relationships(path) | {type: type(r)}] AS rels, "
        "length(path) AS depth",
        {"from": from_entity, "to": to_entity},
    )

    if not paths:
        return {"from": from_entity, "to": to_entity, "found": False, "path": [], "depth": 0}

    p = paths[0]
    steps = []
    for i, node in enumerate(p["nodes"]):
        steps.append({"type": "node", "name": node["name"], "label": node["label"]})
        if i < len(p["rels"]):
            steps.append({"type": "relationship", "relationship": p["rels"][i]["type"]})

    return {
        "from": from_entity,
        "to": to_entity,
        "found": True,
        "depth": p["depth"],
        "steps": steps,
        "nodes": p["nodes"],
        "relationships": p["rels"],
    }


def find_all_paths(from_entity: str, to_entity: str, max_depth: int = 5, limit: int = 10) -> dict:
    paths = neo4j_client.run_query(
        "MATCH path = (a)-[*1.." + str(min(max_depth, 6)) + "]-(b) "
        "WHERE toLower(a.name) CONTAINS toLower($from) "
        "AND toLower(b.name) CONTAINS toLower($to) "
        "RETURN [n IN nodes(path) | {name: n.name, label: labels(n)[0]}] AS nodes, "
        "[r IN relationships(path) | {type: type(r)}] AS rels, "
        "length(path) AS depth "
        "ORDER BY depth LIMIT $limit",
        {"from": from_entity, "to": to_entity, "limit": limit},
    )

    return {
        "from": from_entity,
        "to": to_entity,
        "paths_found": len(paths),
        "paths": [
            {
                "depth": p["depth"],
                "nodes": p["nodes"],
                "relationships": p["rels"],
            }
            for p in paths
        ],
    }
