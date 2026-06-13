from backend.neo4j_client import neo4j_client


def get_source_scores() -> list[dict]:
    sources = neo4j_client.run_query(
        "MATCH (n) WHERE n._source IS NOT NULL "
        "RETURN n._source AS source, "
        "count(n) AS entity_count, "
        "collect(n._confidence) AS confidences "
        "ORDER BY entity_count DESC"
    )

    scored = []
    for s in sources:
        confs = [c for c in s["confidences"] if c]
        high = sum(1 for c in confs if c == "high")
        medium = sum(1 for c in confs if c == "medium")
        low = sum(1 for c in confs if c == "low")
        total = len(confs) if confs else 1

        score = (high * 1.0 + medium * 0.6 + low * 0.2) / total if total else 0

        rel_count = neo4j_client.run_query(
            "MATCH ()-[r]->() WHERE r._source = $source RETURN count(r) AS count",
            {"source": s["source"]},
        )

        scored.append({
            "source": s["source"],
            "reliability_score": round(score, 2),
            "entity_count": s["entity_count"],
            "relationship_count": rel_count[0]["count"] if rel_count else 0,
            "confidence_breakdown": {"high": high, "medium": medium, "low": low},
        })

    scored.sort(key=lambda x: -x["reliability_score"])
    return scored


def get_source_detail(source_name: str) -> dict:
    entities = neo4j_client.run_query(
        "MATCH (n) WHERE n._source = $source "
        "RETURN n.name AS name, labels(n)[0] AS label, n._confidence AS confidence "
        "ORDER BY n.name LIMIT 50",
        {"source": source_name},
    )

    rels = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) WHERE r._source = $source "
        "RETURN a.name AS from, type(r) AS type, b.name AS to, r._confidence AS confidence "
        "LIMIT 50",
        {"source": source_name},
    )

    return {
        "source": source_name,
        "entities": entities,
        "relationships": rels,
        "entity_count": len(entities),
        "relationship_count": len(rels),
    }
