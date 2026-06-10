import json
import csv
import io

from backend.neo4j_client import neo4j_client


def export_json():
    nodes_raw = neo4j_client.run_query(
        "MATCH (n) RETURN n, labels(n) AS labels, n.id AS id LIMIT 5000"
    )
    rels_raw = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) "
        "RETURN a.name AS from_name, labels(a)[0] AS from_label, "
        "type(r) AS rel_type, properties(r) AS rel_props, "
        "b.name AS to_name, labels(b)[0] AS to_label LIMIT 10000"
    )

    nodes = []
    for rec in nodes_raw:
        node = dict(rec["n"])
        node["labels"] = rec["labels"]
        nodes.append(node)

    relationships = []
    for rec in rels_raw:
        relationships.append({
            "from": rec["from_name"],
            "from_label": rec["from_label"],
            "to": rec["to_name"],
            "to_label": rec["to_label"],
            "type": rec["rel_type"],
            "properties": dict(rec["rel_props"] or {}),
        })

    return json.dumps({"nodes": nodes, "relationships": relationships}, indent=2, default=str)


def export_csv():
    nodes_raw = neo4j_client.run_query(
        "MATCH (n) RETURN n.name AS name, labels(n)[0] AS label, "
        "n.id AS id, properties(n) AS props LIMIT 5000"
    )
    rels_raw = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) "
        "RETURN a.name AS from_name, type(r) AS type, b.name AS to_name "
        "LIMIT 10000"
    )

    nodes_buf = io.StringIO()
    w = csv.writer(nodes_buf)
    w.writerow(["name", "label", "id"])
    for rec in nodes_raw:
        w.writerow([rec["name"], rec["label"], rec["id"]])

    rels_buf = io.StringIO()
    w = csv.writer(rels_buf)
    w.writerow(["from", "type", "to"])
    for rec in rels_raw:
        w.writerow([rec["from_name"], rec["type"], rec["to_name"]])

    return {
        "nodes_csv": nodes_buf.getvalue(),
        "relationships_csv": rels_buf.getvalue(),
    }


def export_graphml():
    nodes_raw = neo4j_client.run_query(
        "MATCH (n) RETURN n.name AS name, labels(n)[0] AS label, n.id AS id LIMIT 5000"
    )
    rels_raw = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) "
        "RETURN a.id AS source_id, b.id AS target_id, type(r) AS rel_type LIMIT 10000"
    )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphstruct.org/graphml">',
        '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
        '  <key id="name" for="node" attr.name="name" attr.type="string"/>',
        '  <key id="rel_type" for="edge" attr.name="rel_type" attr.type="string"/>',
        '  <graph id="G" edgedefault="directed">',
    ]

    for rec in nodes_raw:
        nid = rec["id"] or rec["name"]
        name = (rec["name"] or "").replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
        label = (rec["label"] or "").replace("&", "&amp;")
        lines.append(f'    <node id="{nid}">')
        lines.append(f'      <data key="name">{name}</data>')
        lines.append(f'      <data key="label">{label}</data>')
        lines.append("    </node>")

    for i, rec in enumerate(rels_raw):
        src = rec["source_id"] or ""
        tgt = rec["target_id"] or ""
        rt = (rec["rel_type"] or "").replace("&", "&amp;")
        lines.append(f'    <edge id="e{i}" source="{src}" target="{tgt}">')
        lines.append(f'      <data key="rel_type">{rt}</data>')
        lines.append("    </edge>")

    lines.append("  </graph>")
    lines.append("</graphml>")
    return "\n".join(lines)


def export_cypher():
    nodes_raw = neo4j_client.run_query(
        "MATCH (n) RETURN n.name AS name, labels(n)[0] AS label, properties(n) AS props LIMIT 5000"
    )
    rels_raw = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) "
        "RETURN a.name AS from_name, labels(a)[0] AS from_label, "
        "type(r) AS rel_type, "
        "b.name AS to_name, labels(b)[0] AS to_label LIMIT 10000"
    )

    statements = []
    for rec in nodes_raw:
        name = rec["name"]
        label = rec["label"]
        props = dict(rec["props"] or {})
        props.pop("id", None)
        props_str = json.dumps(props, default=str)
        safe_name = name.replace("'", "\\'")
        statements.append(f"MERGE (n:{label} {{name: '{safe_name}'}}) SET n += {props_str};")

    for rec in rels_raw:
        fn = rec["from_name"].replace("'", "\\'")
        tn = rec["to_name"].replace("'", "\\'")
        fl = rec["from_label"]
        tl = rec["to_label"]
        rt = rec["rel_type"]
        statements.append(
            f"MATCH (a:{fl} {{name: '{fn}'}}), (b:{tl} {{name: '{tn}'}}) MERGE (a)-[:{rt}]->(b);"
        )

    return "\n".join(statements)


def export_markdown():
    from backend.services.graph_algorithms import get_graph_health

    health = get_graph_health()
    nodes_raw = neo4j_client.run_query(
        "MATCH (n) RETURN n.name AS name, labels(n)[0] AS label, "
        "size([(n)-[]-() | 1]) AS connections "
        "ORDER BY connections DESC LIMIT 100"
    )
    rels_raw = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) "
        "RETURN a.name AS from_name, type(r) AS type, b.name AS to_name "
        "LIMIT 200"
    )

    lines = [
        "# GraphMind Knowledge Graph Report",
        "",
        "## Overview",
        f"- **Total Nodes:** {health['total_nodes']}",
        f"- **Total Relationships:** {health['total_relationships']}",
        f"- **Avg Connections:** {health['avg_connections']}",
        f"- **Graph Density:** {health['density']}",
        "",
        "## Label Distribution",
    ]
    for label, count in health.get("label_counts", {}).items():
        lines.append(f"- **{label}:** {count}")

    lines.extend(["", "## Top Entities"])
    for rec in nodes_raw[:20]:
        lines.append(f"- **{rec['name']}** ({rec['label']}) — {rec['connections']} connections")

    lines.extend(["", "## Relationships"])
    by_type = {}
    for rec in rels_raw:
        by_type.setdefault(rec["type"], []).append(f"{rec['from_name']} → {rec['to_name']}")
    for rtype, pairs in by_type.items():
        lines.append(f"\n### {rtype}")
        for p in pairs[:10]:
            lines.append(f"- {p}")

    return "\n".join(lines)
