from datetime import datetime
from backend.neo4j_client import neo4j_client


def get_graph_at_time(before_timestamp: str) -> dict:
    nodes = neo4j_client.run_query(
        "MATCH (n) WHERE n._extracted_at <= $ts "
        "RETURN n.name AS name, labels(n)[0] AS label, n._extracted_at AS extracted_at",
        {"ts": before_timestamp},
    )

    rels = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) WHERE r._extracted_at <= $ts "
        "RETURN a.name AS source, b.name AS target, type(r) AS type, r._extracted_at AS extracted_at",
        {"ts": before_timestamp},
    )

    return {
        "timestamp": before_timestamp,
        "node_count": len(nodes),
        "relationship_count": len(rels),
        "nodes": nodes[:200],
        "relationships": rels[:500],
    }


def get_growth_timeline(interval: str = "day") -> list[dict]:
    nodes = neo4j_client.run_query(
        "MATCH (n) WHERE n._extracted_at IS NOT NULL "
        "RETURN n._extracted_at AS ts ORDER BY ts"
    )
    rels = neo4j_client.run_query(
        "MATCH ()-[r]->() WHERE r._extracted_at IS NOT NULL "
        "RETURN r._extracted_at AS ts ORDER BY ts"
    )

    buckets = {}

    for n in nodes:
        key = _bucket_key(n["ts"], interval)
        if key:
            buckets.setdefault(key, {"nodes": 0, "relationships": 0})
            buckets[key]["nodes"] += 1

    for r in rels:
        key = _bucket_key(r["ts"], interval)
        if key:
            buckets.setdefault(key, {"nodes": 0, "relationships": 0})
            buckets[key]["relationships"] += 1

    timeline = []
    cum_nodes = 0
    cum_rels = 0
    for key in sorted(buckets.keys()):
        cum_nodes += buckets[key]["nodes"]
        cum_rels += buckets[key]["relationships"]
        timeline.append({
            "period": key,
            "new_nodes": buckets[key]["nodes"],
            "new_relationships": buckets[key]["relationships"],
            "cumulative_nodes": cum_nodes,
            "cumulative_relationships": cum_rels,
        })

    return timeline


def get_entity_evolution(entity_name: str) -> list[dict]:
    rels = neo4j_client.run_query(
        "MATCH (n)-[r]-(m) WHERE toLower(n.name) CONTAINS toLower($name) "
        "AND r._extracted_at IS NOT NULL "
        "RETURN type(r) AS type, m.name AS related, r._extracted_at AS ts, "
        "startNode(r).name = n.name AS outgoing "
        "ORDER BY r._extracted_at",
        {"name": entity_name},
    )

    evolution = []
    for r in rels:
        direction = "outgoing" if r["outgoing"] else "incoming"
        evolution.append({
            "timestamp": r["ts"],
            "relationship": r["type"],
            "related_entity": r["related"],
            "direction": direction,
        })

    return evolution


def _bucket_key(ts: str, interval: str) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return ts[:10] if isinstance(ts, str) else ""

    if interval == "hour":
        return dt.strftime("%Y-%m-%d %H:00")
    elif interval == "day":
        return dt.strftime("%Y-%m-%d")
    elif interval == "week":
        return dt.strftime("%Y-W%W")
    elif interval == "month":
        return dt.strftime("%Y-%m")
    return dt.strftime("%Y-%m-%d")
