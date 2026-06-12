import json
from datetime import datetime
from io import BytesIO
from backend.neo4j_client import neo4j_client


def generate_text_report() -> str:
    stats = _get_graph_stats()
    top_entities = _get_top_entities()
    rel_types = _get_relationship_types()

    lines = [
        "=" * 60,
        "GRAPHMIND KNOWLEDGE GRAPH REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        "GRAPH OVERVIEW",
        "-" * 40,
        f"Total Nodes:         {stats.get('total_nodes', 0)}",
        f"Total Relationships: {stats.get('total_relationships', 0)}",
        f"Entity Types:        {stats.get('label_count', 0)}",
        f"Relationship Types:  {stats.get('rel_type_count', 0)}",
        "",
        "ENTITY TYPE DISTRIBUTION",
        "-" * 40,
    ]

    for lt in stats.get("labels", []):
        lines.append(f"  {lt['label']:30s} {lt['count']:>6d}")

    lines.extend(["", "RELATIONSHIP TYPE DISTRIBUTION", "-" * 40])
    for rt in rel_types:
        lines.append(f"  {rt['type']:30s} {rt['count']:>6d}")

    lines.extend(["", "TOP ENTITIES BY CONNECTIVITY", "-" * 40])
    for i, e in enumerate(top_entities, 1):
        lines.append(f"  {i:>2}. {e['name']:30s} ({e['label']}) — {e['degree']} connections")

    lines.extend([
        "",
        "=" * 60,
        "End of Report",
    ])

    return "\n".join(lines)


def generate_json_report() -> dict:
    stats = _get_graph_stats()
    top_entities = _get_top_entities()
    rel_types = _get_relationship_types()

    return {
        "report_type": "knowledge_graph_summary",
        "generated_at": datetime.now().isoformat(),
        "overview": stats,
        "relationship_types": rel_types,
        "top_entities": top_entities,
    }


def generate_html_report() -> str:
    stats = _get_graph_stats()
    top_entities = _get_top_entities()
    rel_types = _get_relationship_types()

    labels_rows = "".join(
        f"<tr><td>{lt['label']}</td><td>{lt['count']}</td></tr>"
        for lt in stats.get("labels", [])
    )
    rels_rows = "".join(
        f"<tr><td>{rt['type']}</td><td>{rt['count']}</td></tr>"
        for rt in rel_types
    )
    entities_rows = "".join(
        f"<tr><td>{i}</td><td>{e['name']}</td><td>{e['label']}</td><td>{e['degree']}</td></tr>"
        for i, e in enumerate(top_entities, 1)
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<title>GraphMind Report</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; color: #e6edf3; background: #0d1117; padding: 20px; }}
  h1 {{ color: #c9d1d9; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
  h2 {{ color: #8b949e; margin-top: 30px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
  th, td {{ border: 1px solid #30363d; padding: 8px 12px; text-align: left; }}
  th {{ background: #161b22; color: #c9d1d9; }}
  .stat {{ display: inline-block; background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px 25px; margin: 5px; text-align: center; }}
  .stat-value {{ font-size: 24px; font-weight: bold; color: #a78bfa; }}
  .stat-label {{ font-size: 12px; color: #8b949e; }}
</style>
</head>
<body>
<h1>GraphMind Knowledge Graph Report</h1>
<p style="color: #8b949e;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<div>
  <div class="stat"><div class="stat-value">{stats.get('total_nodes', 0)}</div><div class="stat-label">Nodes</div></div>
  <div class="stat"><div class="stat-value">{stats.get('total_relationships', 0)}</div><div class="stat-label">Relationships</div></div>
  <div class="stat"><div class="stat-value">{stats.get('label_count', 0)}</div><div class="stat-label">Entity Types</div></div>
  <div class="stat"><div class="stat-value">{stats.get('rel_type_count', 0)}</div><div class="stat-label">Rel Types</div></div>
</div>

<h2>Entity Types</h2>
<table><tr><th>Type</th><th>Count</th></tr>{labels_rows}</table>

<h2>Relationship Types</h2>
<table><tr><th>Type</th><th>Count</th></tr>{rels_rows}</table>

<h2>Top Entities</h2>
<table><tr><th>#</th><th>Name</th><th>Type</th><th>Connections</th></tr>{entities_rows}</table>
</body>
</html>"""


def _get_graph_stats() -> dict:
    nodes = neo4j_client.run_query("MATCH (n) RETURN count(n) AS count")
    rels = neo4j_client.run_query("MATCH ()-[r]->() RETURN count(r) AS count")
    labels = neo4j_client.run_query(
        "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC"
    )
    rel_types = neo4j_client.run_query(
        "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY count DESC"
    )

    return {
        "total_nodes": nodes[0]["count"] if nodes else 0,
        "total_relationships": rels[0]["count"] if rels else 0,
        "label_count": len(labels),
        "rel_type_count": len(rel_types),
        "labels": labels,
    }


def _get_top_entities(limit: int = 15) -> list[dict]:
    return neo4j_client.run_query(
        "MATCH (n)-[r]-() "
        "WITH n, count(r) AS degree, labels(n)[0] AS label "
        "RETURN n.name AS name, label, degree "
        "ORDER BY degree DESC LIMIT $limit",
        {"limit": limit},
    )


def _get_relationship_types() -> list[dict]:
    return neo4j_client.run_query(
        "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY count DESC"
    )
