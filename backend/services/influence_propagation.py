from backend.neo4j_client import neo4j_client


def calculate_influence(entity_name: str, max_depth: int = 3) -> dict:
    node = neo4j_client.run_query(
        "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN n.name AS name, labels(n)[0] AS label LIMIT 1",
        {"name": entity_name},
    )
    if not node:
        return {"entity": entity_name, "influence_score": 0, "reach": {}}

    actual_name = node[0]["name"]
    label = node[0]["label"]

    layers = {}
    visited = {actual_name}

    current_names = [actual_name]
    for depth in range(1, max_depth + 1):
        if not current_names:
            break

        placeholders = ", ".join(f"$n{i}" for i in range(len(current_names)))
        params = {f"n{i}": name for i, name in enumerate(current_names)}

        neighbors = neo4j_client.run_query(
            f"MATCH (a)-[r]-(b) WHERE a.name IN [{placeholders}] AND NOT b.name IN $visited "
            f"RETURN DISTINCT b.name AS name, labels(b)[0] AS label, type(r) AS via",
            {**params, "visited": list(visited)},
        )

        layer_nodes = []
        next_names = []
        for n in neighbors:
            if n["name"] not in visited:
                visited.add(n["name"])
                layer_nodes.append({
                    "name": n["name"],
                    "label": n["label"],
                    "connected_via": n["via"],
                })
                next_names.append(n["name"])

        layers[f"depth_{depth}"] = layer_nodes
        current_names = next_names

    total_reach = sum(len(v) for v in layers.values())
    weighted_reach = sum(len(v) / (i + 1) for i, v in enumerate(layers.values()))

    return {
        "entity": actual_name,
        "label": label,
        "influence_score": round(weighted_reach, 2),
        "total_reach": total_reach,
        "layers": layers,
        "depth_analyzed": max_depth,
    }


def find_most_influential(top_n: int = 10) -> list[dict]:
    nodes = neo4j_client.run_query(
        "MATCH (n)-[r]-() "
        "WITH n, count(r) AS degree, labels(n)[0] AS label "
        "RETURN n.name AS name, label, degree "
        "ORDER BY degree DESC LIMIT $limit",
        {"limit": top_n},
    )

    results = []
    for n in nodes:
        influence = calculate_influence(n["name"], max_depth=2)
        results.append({
            "name": n["name"],
            "label": n["label"],
            "degree": n["degree"],
            "influence_score": influence["influence_score"],
            "total_reach": influence["total_reach"],
        })

    results.sort(key=lambda x: x["influence_score"], reverse=True)
    return results
