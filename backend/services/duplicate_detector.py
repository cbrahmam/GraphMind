from difflib import SequenceMatcher
from backend.neo4j_client import neo4j_client


def find_duplicates(threshold: float = 0.8) -> list[dict]:
    nodes = neo4j_client.run_query(
        "MATCH (n) WHERE n.name IS NOT NULL "
        "RETURN n.name AS name, labels(n)[0] AS label, id(n) AS node_id "
        "ORDER BY n.name"
    )

    duplicates = []
    seen = set()

    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            pair_key = (min(a["node_id"], b["node_id"]), max(a["node_id"], b["node_id"]))
            if pair_key in seen:
                continue

            if a["name"].lower() == b["name"].lower():
                seen.add(pair_key)
                duplicates.append({
                    "entity_a": {"name": a["name"], "label": a["label"], "id": a["node_id"]},
                    "entity_b": {"name": b["name"], "label": b["label"], "id": b["node_id"]},
                    "similarity": 1.0,
                    "match_type": "exact_case_insensitive",
                })
                continue

            ratio = SequenceMatcher(None, a["name"].lower(), b["name"].lower()).ratio()
            if ratio >= threshold:
                seen.add(pair_key)
                duplicates.append({
                    "entity_a": {"name": a["name"], "label": a["label"], "id": a["node_id"]},
                    "entity_b": {"name": b["name"], "label": b["label"], "id": b["node_id"]},
                    "similarity": round(ratio, 3),
                    "match_type": "fuzzy",
                })

        if len(duplicates) >= 50:
            break

    duplicates.sort(key=lambda d: -d["similarity"])
    return duplicates


def merge_entities(keep_id: int, remove_id: int) -> dict:
    keep = neo4j_client.run_query(
        "MATCH (n) WHERE id(n) = $id RETURN n.name AS name, labels(n)[0] AS label",
        {"id": keep_id},
    )
    remove = neo4j_client.run_query(
        "MATCH (n) WHERE id(n) = $id RETURN n.name AS name, labels(n)[0] AS label",
        {"id": remove_id},
    )

    if not keep or not remove:
        return {"merged": False, "error": "Entity not found"}

    neo4j_client.run_query(
        "MATCH (old) WHERE id(old) = $remove_id "
        "MATCH (keep) WHERE id(keep) = $keep_id "
        "OPTIONAL MATCH (old)-[r]->() "
        "WITH old, keep, collect(r) AS rels_out "
        "OPTIONAL MATCH ()-[r]->(old) "
        "WITH old, keep, rels_out, collect(r) AS rels_in "
        "FOREACH (r IN rels_out | "
        "  CREATE (keep)-[nr:MERGED_FROM]->(endNode(r)) "
        ") "
        "FOREACH (r IN rels_in | "
        "  CREATE (startNode(r))-[nr:MERGED_FROM]->(keep) "
        ") "
        "DETACH DELETE old",
        {"keep_id": keep_id, "remove_id": remove_id},
    )

    return {
        "merged": True,
        "kept": {"name": keep[0]["name"], "label": keep[0]["label"]},
        "removed": {"name": remove[0]["name"], "label": remove[0]["label"]},
    }


def get_duplicate_stats() -> dict:
    total = neo4j_client.run_query("MATCH (n) RETURN count(n) AS count")
    total_count = total[0]["count"] if total else 0

    exact_dupes = neo4j_client.run_query(
        "MATCH (a), (b) WHERE id(a) < id(b) AND toLower(a.name) = toLower(b.name) "
        "RETURN count(*) AS count"
    )

    return {
        "total_entities": total_count,
        "exact_duplicates": exact_dupes[0]["count"] if exact_dupes else 0,
    }
