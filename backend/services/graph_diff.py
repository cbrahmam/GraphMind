from backend.neo4j_client import neo4j_client


def snapshot_graph() -> dict:
    nodes = neo4j_client.run_query(
        "MATCH (n) RETURN n.name AS name, labels(n)[0] AS label, n.id AS id"
    )
    rels = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) RETURN a.name AS from_name, type(r) AS type, b.name AS to_name"
    )
    return {
        "nodes": {f"{n['name']}::{n['label']}": n for n in nodes},
        "relationships": {f"{r['from_name']}-[{r['type']}]->{r['to_name']}": r for r in rels},
    }


def compute_diff(before: dict, after: dict) -> dict:
    before_nodes = set(before.get("nodes", {}).keys())
    after_nodes = set(after.get("nodes", {}).keys())
    before_rels = set(before.get("relationships", {}).keys())
    after_rels = set(after.get("relationships", {}).keys())

    new_nodes = after_nodes - before_nodes
    removed_nodes = before_nodes - after_nodes
    new_rels = after_rels - before_rels
    removed_rels = before_rels - after_rels

    updated_nodes = []
    for key in after_nodes & before_nodes:
        bn = before["nodes"][key]
        an = after["nodes"][key]
        if bn != an:
            updated_nodes.append(key)

    return {
        "new_nodes": [after["nodes"][k] for k in new_nodes],
        "removed_nodes": [before["nodes"][k] for k in removed_nodes],
        "updated_nodes": updated_nodes,
        "new_relationships": [after["relationships"][k] for k in new_rels],
        "removed_relationships": [before["relationships"][k] for k in removed_rels],
        "summary": {
            "nodes_added": len(new_nodes),
            "nodes_removed": len(removed_nodes),
            "nodes_updated": len(updated_nodes),
            "relationships_added": len(new_rels),
            "relationships_removed": len(removed_rels),
        },
    }
