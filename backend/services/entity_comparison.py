from backend.neo4j_client import neo4j_client


def compare_entities(entity_a: str, entity_b: str) -> dict:
    def get_entity_data(name):
        node = neo4j_client.run_query(
            "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
            "RETURN n AS props, labels(n) AS labels LIMIT 1",
            {"name": name},
        )
        if not node:
            return None

        properties = {k: v for k, v in dict(node[0]["props"]).items() if not k.startswith("_") and k != "id"}
        label = node[0]["labels"][0] if node[0]["labels"] else ""

        rels = neo4j_client.run_query(
            "MATCH (n)-[r]-(m) WHERE toLower(n.name) CONTAINS toLower($name) "
            "RETURN type(r) AS type, m.name AS related, labels(m)[0] AS related_label, "
            "startNode(r).name = n.name AS outgoing",
            {"name": name},
        )

        neighbors = neo4j_client.run_query(
            "MATCH (n)-[]-(m) WHERE toLower(n.name) CONTAINS toLower($name) "
            "RETURN DISTINCT m.name AS name",
            {"name": name},
        )

        return {
            "name": dict(node[0]["props"]).get("name", name),
            "label": label,
            "properties": properties,
            "relationships": [
                {"type": r["type"], "related": r["related"], "direction": "out" if r["outgoing"] else "in"}
                for r in rels
            ],
            "neighbor_names": {n["name"] for n in neighbors},
            "degree": len(rels),
        }

    data_a = get_entity_data(entity_a)
    data_b = get_entity_data(entity_b)

    if not data_a or not data_b:
        missing = entity_a if not data_a else entity_b
        return {"error": f"Entity '{missing}' not found"}

    shared_neighbors = data_a["neighbor_names"] & data_b["neighbor_names"]
    unique_a = data_a["neighbor_names"] - data_b["neighbor_names"]
    unique_b = data_b["neighbor_names"] - data_a["neighbor_names"]

    shared_rel_types = {r["type"] for r in data_a["relationships"]} & {r["type"] for r in data_b["relationships"]}

    common_props = set(data_a["properties"].keys()) & set(data_b["properties"].keys())
    prop_comparison = {}
    for prop in common_props:
        prop_comparison[prop] = {
            "entity_a": data_a["properties"][prop],
            "entity_b": data_b["properties"][prop],
            "match": data_a["properties"][prop] == data_b["properties"][prop],
        }

    similarity = 0
    total_neighbors = len(data_a["neighbor_names"] | data_b["neighbor_names"])
    if total_neighbors > 0:
        similarity = len(shared_neighbors) / total_neighbors

    del data_a["neighbor_names"]
    del data_b["neighbor_names"]

    return {
        "entity_a": data_a,
        "entity_b": data_b,
        "comparison": {
            "shared_neighbors": sorted(shared_neighbors)[:20],
            "unique_to_a": sorted(unique_a)[:15],
            "unique_to_b": sorted(unique_b)[:15],
            "shared_relationship_types": sorted(shared_rel_types),
            "property_comparison": prop_comparison,
            "jaccard_similarity": round(similarity, 3),
            "same_type": data_a["label"] == data_b["label"],
        },
    }
