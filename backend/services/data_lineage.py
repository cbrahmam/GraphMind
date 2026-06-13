from backend.neo4j_client import neo4j_client


def get_entity_lineage(entity_name: str) -> dict:
    node = neo4j_client.run_query(
        "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN n AS props, labels(n)[0] AS label LIMIT 1",
        {"name": entity_name},
    )
    if not node:
        return {"entity": entity_name, "found": False, "sources": []}

    props = dict(node[0]["props"])
    source = props.get("_source", "unknown")
    confidence = props.get("_confidence", "unknown")
    extracted_at = props.get("_extracted_at", "unknown")

    rels = neo4j_client.run_query(
        "MATCH (n)-[r]-(m) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN type(r) AS type, m.name AS related, "
        "r._source AS source, r._confidence AS confidence, r._extracted_at AS extracted_at",
        {"name": entity_name},
    )

    sources = set()
    sources.add(source)
    for r in rels:
        if r.get("source"):
            sources.add(r["source"])

    return {
        "entity": props.get("name", entity_name),
        "label": node[0]["label"],
        "found": True,
        "entity_source": source,
        "entity_confidence": confidence,
        "entity_extracted_at": extracted_at,
        "relationship_lineage": [
            {
                "type": r["type"],
                "related": r["related"],
                "source": r.get("source", "unknown"),
                "confidence": r.get("confidence", "unknown"),
                "extracted_at": r.get("extracted_at", "unknown"),
            }
            for r in rels
        ],
        "all_sources": sorted(sources - {"unknown", None}),
        "total_facts": 1 + len(rels),
    }


def get_source_summary() -> dict:
    sources = neo4j_client.run_query(
        "MATCH (n) WHERE n._source IS NOT NULL "
        "RETURN n._source AS source, count(n) AS entity_count "
        "ORDER BY entity_count DESC"
    )

    rel_sources = neo4j_client.run_query(
        "MATCH ()-[r]->() WHERE r._source IS NOT NULL "
        "RETURN r._source AS source, count(r) AS rel_count "
        "ORDER BY rel_count DESC"
    )

    source_map = {}
    for s in sources:
        source_map.setdefault(s["source"], {"entities": 0, "relationships": 0})
        source_map[s["source"]]["entities"] = s["entity_count"]
    for r in rel_sources:
        source_map.setdefault(r["source"], {"entities": 0, "relationships": 0})
        source_map[r["source"]]["relationships"] = r["rel_count"]

    return {
        "sources": [
            {"source": k, "entities": v["entities"], "relationships": v["relationships"],
             "total_facts": v["entities"] + v["relationships"]}
            for k, v in sorted(source_map.items(), key=lambda x: -(x[1]["entities"] + x[1]["relationships"]))
        ],
        "total_sources": len(source_map),
    }
