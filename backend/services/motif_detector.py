from backend.neo4j_client import neo4j_client


def find_triangles(limit: int = 20) -> list[dict]:
    triangles = neo4j_client.run_query(
        "MATCH (a)-[r1]-(b)-[r2]-(c)-[r3]-(a) "
        "WHERE id(a) < id(b) AND id(b) < id(c) "
        "RETURN a.name AS node_a, labels(a)[0] AS label_a, "
        "b.name AS node_b, labels(b)[0] AS label_b, "
        "c.name AS node_c, labels(c)[0] AS label_c, "
        "type(r1) AS rel_ab, type(r2) AS rel_bc, type(r3) AS rel_ca "
        "LIMIT $limit",
        {"limit": limit},
    )

    return [
        {
            "type": "triangle",
            "nodes": [
                {"name": t["node_a"], "label": t["label_a"]},
                {"name": t["node_b"], "label": t["label_b"]},
                {"name": t["node_c"], "label": t["label_c"]},
            ],
            "relationships": [t["rel_ab"], t["rel_bc"], t["rel_ca"]],
        }
        for t in triangles
    ]


def find_star_patterns(min_degree: int = 5, limit: int = 15) -> list[dict]:
    stars = neo4j_client.run_query(
        "MATCH (center)-[r]-(leaf) "
        "WITH center, count(r) AS degree, labels(center)[0] AS label, "
        "collect({name: leaf.name, label: labels(leaf)[0], type: type(r)})[..10] AS leaves "
        "WHERE degree >= $min "
        "RETURN center.name AS center, label, degree, leaves "
        "ORDER BY degree DESC LIMIT $limit",
        {"min": min_degree, "limit": limit},
    )

    return [
        {
            "type": "star",
            "center": {"name": s["center"], "label": s["label"]},
            "degree": s["degree"],
            "leaves": s["leaves"],
        }
        for s in stars
    ]


def find_chains(min_length: int = 4, limit: int = 10) -> list[dict]:
    chains = neo4j_client.run_query(
        "MATCH path = (a)-[*" + str(min_length) + ".." + str(min_length + 2) + "]->(b) "
        "WHERE all(n IN nodes(path) WHERE size((n)--()) <= 3) "
        "RETURN [n IN nodes(path) | {name: n.name, label: labels(n)[0]}] AS nodes, "
        "[r IN relationships(path) | type(r)] AS rels, length(path) AS len "
        "LIMIT $limit",
        {"limit": limit},
    )

    return [
        {
            "type": "chain",
            "length": c["len"],
            "nodes": c["nodes"],
            "relationships": c["rels"],
        }
        for c in chains
    ]


def find_all_motifs() -> dict:
    triangles = find_triangles()
    stars = find_star_patterns()
    chains = find_chains()

    return {
        "triangles": {"count": len(triangles), "motifs": triangles},
        "stars": {"count": len(stars), "motifs": stars},
        "chains": {"count": len(chains), "motifs": chains},
        "total_motifs": len(triangles) + len(stars) + len(chains),
    }
