import json
from backend.neo4j_client import neo4j_client


def flexible_query(
    node_types: list[str] | None = None,
    relationship_types: list[str] | None = None,
    properties: dict | None = None,
    limit: int = 50,
    offset: int = 0,
    order_by: str | None = None,
    include_relationships: bool = True,
) -> dict:
    where_clauses = []
    params = {"limit": limit, "offset": offset}

    if node_types:
        label_filter = " OR ".join(f"n:{lt}" for lt in node_types)
        where_clauses.append(f"({label_filter})")

    if properties:
        for key, value in properties.items():
            param_key = f"prop_{key}"
            if isinstance(value, str) and value.startswith("~"):
                where_clauses.append(f"toLower(n.{key}) CONTAINS toLower(${param_key})")
                params[param_key] = value[1:]
            else:
                where_clauses.append(f"n.{key} = ${param_key}")
                params[param_key] = value

    where = " AND ".join(where_clauses) if where_clauses else "true"

    order = f"ORDER BY n.{order_by}" if order_by else "ORDER BY n.name"

    nodes = neo4j_client.run_query(
        f"MATCH (n) WHERE {where} "
        f"RETURN n AS props, labels(n) AS labels, id(n) AS id "
        f"{order} SKIP $offset LIMIT $limit",
        params,
    )

    count_result = neo4j_client.run_query(
        f"MATCH (n) WHERE {where} RETURN count(n) AS total",
        params,
    )
    total = count_result[0]["total"] if count_result else 0

    results = []
    for n in nodes:
        props = {k: v for k, v in dict(n["props"]).items() if not k.startswith("_")}
        entry = {
            "id": n["id"],
            "labels": n["labels"],
            "properties": props,
        }

        if include_relationships:
            rels = neo4j_client.run_query(
                "MATCH (n)-[r]-(m) WHERE id(n) = $id "
                "RETURN type(r) AS type, m.name AS related, labels(m)[0] AS related_label, "
                "startNode(r) = n AS outgoing LIMIT 20",
                {"id": n["id"]},
            )
            if relationship_types:
                rels = [r for r in rels if r["type"] in relationship_types]
            entry["relationships"] = [
                {"type": r["type"], "related": r["related"], "label": r["related_label"],
                 "direction": "out" if r["outgoing"] else "in"}
                for r in rels
            ]

        results.append(entry)

    return {
        "data": results,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total,
    }


def introspect_schema() -> dict:
    labels = neo4j_client.run_query(
        "CALL db.labels() YIELD label "
        "RETURN label ORDER BY label"
    )
    rel_types = neo4j_client.run_query(
        "CALL db.relationshipTypes() YIELD relationshipType "
        "RETURN relationshipType ORDER BY relationshipType"
    )

    schema = {"types": {}, "relationships": []}

    for l in labels:
        label = l["label"]
        props = neo4j_client.run_query(
            f"MATCH (n:{label}) "
            "WITH keys(n) AS allKeys "
            "UNWIND allKeys AS key "
            "RETURN DISTINCT key ORDER BY key"
        )
        schema["types"][label] = {
            "properties": [p["key"] for p in props if not p["key"].startswith("_")],
        }

    for r in rel_types:
        schema["relationships"].append(r["relationshipType"])

    return schema
