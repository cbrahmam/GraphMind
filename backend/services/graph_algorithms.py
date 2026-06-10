from backend.neo4j_client import neo4j_client


def run_centrality(algorithm="degree", label=None):
    label_filter = f":{label}" if label else ""

    if algorithm == "degree":
        cypher = (
            f"MATCH (n{label_filter})-[r]-() "
            "WITH n, count(r) AS degree "
            "RETURN n.name AS node_name, labels(n)[0] AS label, degree AS score "
            "ORDER BY score DESC LIMIT 20"
        )
    elif algorithm == "pagerank":
        cypher = (
            f"MATCH (n{label_filter}) "
            "WITH n, size([(n)-[]-() | 1]) AS connections "
            "OPTIONAL MATCH (n)<-[r]-() "
            "WITH n, connections, count(r) AS incoming "
            "WITH n, connections, incoming, "
            "(incoming * 1.0 / CASE WHEN connections = 0 THEN 1 ELSE connections END) + connections * 0.15 AS pr_score "
            "RETURN n.name AS node_name, labels(n)[0] AS label, pr_score AS score "
            "ORDER BY score DESC LIMIT 20"
        )
    elif algorithm == "betweenness":
        cypher = (
            f"MATCH (n{label_filter}) "
            "WITH n "
            "OPTIONAL MATCH (a)-[*1..3]-(n)-[*1..3]-(b) "
            "WHERE a <> b AND a <> n AND b <> n "
            "WITH n, count(DISTINCT [a, b]) AS paths_through "
            "RETURN n.name AS node_name, labels(n)[0] AS label, paths_through AS score "
            "ORDER BY score DESC LIMIT 20"
        )
    else:
        return []

    results = neo4j_client.run_query(cypher)
    return [
        {"node_name": r["node_name"], "label": r["label"], "score": round(r["score"], 4), "rank": i + 1}
        for i, r in enumerate(results)
    ]


def detect_communities():
    cypher = (
        "MATCH (n)-[r]-(m) "
        "WHERE id(n) < id(m) "
        "WITH n, m, labels(n)[0] AS n_label, labels(m)[0] AS m_label "
        "RETURN n.name AS from_name, n_label AS from_label, "
        "m.name AS to_name, m_label AS to_label"
    )
    edges = neo4j_client.run_query(cypher)

    if not edges:
        return []

    adjacency = {}
    node_labels = {}
    for e in edges:
        adjacency.setdefault(e["from_name"], set()).add(e["to_name"])
        adjacency.setdefault(e["to_name"], set()).add(e["from_name"])
        node_labels[e["from_name"]] = e["from_label"]
        node_labels[e["to_name"]] = e["to_label"]

    visited = set()
    communities = []

    for node in adjacency:
        if node in visited:
            continue
        queue = [node]
        community_nodes = []
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            community_nodes.append(current)
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)

        if community_nodes:
            labels_in = [node_labels.get(n, "") for n in community_nodes]
            from collections import Counter
            label_counter = Counter(labels_in)
            dominant = label_counter.most_common(1)[0][0] if label_counter else ""

            internal = 0
            external = 0
            comm_set = set(community_nodes)
            for n in community_nodes:
                for neighbor in adjacency.get(n, []):
                    if neighbor in comm_set:
                        internal += 1
                    else:
                        external += 1
            internal //= 2

            communities.append({
                "id": len(communities),
                "node_count": len(community_nodes),
                "nodes": [{"name": n, "label": node_labels.get(n, "")} for n in community_nodes[:50]],
                "dominant_label": dominant,
                "suggested_name": f"{dominant} cluster ({len(community_nodes)} entities)",
                "internal_relationships": internal,
                "external_relationships": external,
            })

    communities.sort(key=lambda c: c["node_count"], reverse=True)
    return communities


def find_similar(node_name, label=None, top_n=5):
    if label:
        cypher = (
            f"MATCH (target:{label} {{name: $name}})-[r]-(neighbor) "
            f"MATCH (other:{label})-[r2]-(neighbor) "
            "WHERE other.name <> target.name "
            "WITH other, count(DISTINCT neighbor) AS shared "
            "RETURN other.name AS node_name, labels(other)[0] AS label, shared AS score "
            "ORDER BY shared DESC LIMIT $limit"
        )
    else:
        cypher = (
            "MATCH (target {name: $name})-[r]-(neighbor) "
            "MATCH (other)-[r2]-(neighbor) "
            "WHERE other.name <> target.name AND labels(other) = labels(target) "
            "WITH other, count(DISTINCT neighbor) AS shared "
            "RETURN other.name AS node_name, labels(other)[0] AS label, shared AS score "
            "ORDER BY shared DESC LIMIT $limit"
        )

    results = neo4j_client.run_query(cypher, {"name": node_name, "limit": top_n})
    return [
        {"node_name": r["node_name"], "label": r["label"], "score": r["score"], "rank": i + 1}
        for i, r in enumerate(results)
    ]


def get_graph_health():
    stats = neo4j_client.get_stats()
    total_nodes = stats.get("total_nodes", 0)
    total_rels = stats.get("total_relationships", 0)

    avg_connections = 0
    if total_nodes > 0:
        avg_connections = round(total_rels * 2 / total_nodes, 2)

    density = 0
    if total_nodes > 1:
        max_edges = total_nodes * (total_nodes - 1)
        density = round(total_rels / max_edges, 6) if max_edges > 0 else 0

    isolated = neo4j_client.run_query(
        "MATCH (n) WHERE NOT (n)-[]-() RETURN count(n) AS count"
    )
    isolated_count = isolated[0]["count"] if isolated else 0

    return {
        "total_nodes": total_nodes,
        "total_relationships": total_rels,
        "avg_connections": avg_connections,
        "density": density,
        "isolated_nodes": isolated_count,
        "label_counts": stats.get("label_counts", {}),
        "relationship_type_counts": stats.get("relationship_type_counts", {}),
    }
