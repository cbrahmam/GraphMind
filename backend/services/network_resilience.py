from backend.neo4j_client import neo4j_client


def find_critical_nodes(top_n: int = 10) -> list[dict]:
    bridges = neo4j_client.run_query(
        "MATCH (n)-[r]-() "
        "WITH n, count(r) AS degree, labels(n)[0] AS label "
        "ORDER BY degree DESC LIMIT 50 "
        "RETURN n.name AS name, label, degree"
    )

    critical = []
    for b in bridges:
        neighbors = neo4j_client.run_query(
            "MATCH (n)-[]-(m) WHERE n.name = $name "
            "RETURN collect(DISTINCT m.name) AS neighbors",
            {"name": b["name"]},
        )
        neighbor_list = neighbors[0]["neighbors"] if neighbors else []

        connected_without = 0
        total_pairs = 0
        sample_neighbors = neighbor_list[:10]
        for i, a in enumerate(sample_neighbors):
            for bb in sample_neighbors[i + 1:]:
                total_pairs += 1
                path = neo4j_client.run_query(
                    "MATCH path = shortestPath((x)-[*1..5]-(y)) "
                    "WHERE x.name = $a AND y.name = $b "
                    "AND NONE(node IN nodes(path) WHERE node.name = $exclude) "
                    "RETURN length(path) AS len",
                    {"a": a, "b": bb, "exclude": b["name"]},
                )
                if path:
                    connected_without += 1

        criticality = 1.0 - (connected_without / total_pairs) if total_pairs > 0 else 1.0

        critical.append({
            "name": b["name"],
            "label": b["label"],
            "degree": b["degree"],
            "criticality_score": round(criticality, 3),
            "neighbor_count": len(neighbor_list),
            "pairs_tested": total_pairs,
            "pairs_disconnected": total_pairs - connected_without,
        })

    critical.sort(key=lambda x: -x["criticality_score"])
    return critical[:top_n]


def analyze_resilience() -> dict:
    total_nodes = neo4j_client.run_query("MATCH (n) RETURN count(n) AS count")
    total_rels = neo4j_client.run_query("MATCH ()-[r]->() RETURN count(r) AS count")
    node_count = total_nodes[0]["count"] if total_nodes else 0
    rel_count = total_rels[0]["count"] if total_rels else 0

    isolated = neo4j_client.run_query(
        "MATCH (n) WHERE NOT (n)-[]-() RETURN count(n) AS count"
    )
    isolated_count = isolated[0]["count"] if isolated else 0

    degree_dist = neo4j_client.run_query(
        "MATCH (n)-[r]-() "
        "WITH n, count(r) AS degree "
        "RETURN min(degree) AS min_deg, max(degree) AS max_deg, "
        "avg(degree) AS avg_deg, stDev(degree) AS std_deg"
    )

    single_point = neo4j_client.run_query(
        "MATCH (a)-[]-(bridge)-[]-(b) "
        "WHERE NOT (a)-[]-(b) AND a <> b AND a <> bridge AND b <> bridge "
        "WITH bridge, count(DISTINCT a) + count(DISTINCT b) AS connections "
        "WHERE connections > 4 "
        "RETURN bridge.name AS name, labels(bridge)[0] AS label, connections "
        "ORDER BY connections DESC LIMIT 5"
    )

    avg_degree = degree_dist[0]["avg_deg"] if degree_dist else 0
    density = (2 * rel_count) / (node_count * (node_count - 1)) if node_count > 1 else 0

    if density > 0.1 and avg_degree > 4:
        resilience_rating = "high"
    elif density > 0.02 and avg_degree > 2:
        resilience_rating = "medium"
    else:
        resilience_rating = "low"

    return {
        "node_count": node_count,
        "relationship_count": rel_count,
        "isolated_nodes": isolated_count,
        "density": round(density, 4),
        "degree_stats": {
            "min": degree_dist[0]["min_deg"] if degree_dist else 0,
            "max": degree_dist[0]["max_deg"] if degree_dist else 0,
            "avg": round(degree_dist[0]["avg_deg"], 2) if degree_dist else 0,
            "std_dev": round(degree_dist[0]["std_deg"], 2) if degree_dist else 0,
        },
        "single_points_of_failure": [
            {"name": s["name"], "label": s["label"], "connections": s["connections"]}
            for s in single_point
        ],
        "resilience_rating": resilience_rating,
    }
