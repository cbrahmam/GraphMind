import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def summarize_full_graph() -> dict:
    labels = neo4j_client.run_query(
        "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC"
    )
    rel_types = neo4j_client.run_query(
        "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY count DESC"
    )
    sample_rels = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) RETURN a.name AS from, labels(a)[0] AS from_label, "
        "type(r) AS type, b.name AS to, labels(b)[0] AS to_label LIMIT 40"
    )
    top_nodes = neo4j_client.run_query(
        "MATCH (n)-[r]-() WITH n, count(r) AS deg, labels(n)[0] AS label "
        "RETURN n.name AS name, label, deg ORDER BY deg DESC LIMIT 15"
    )

    prompt = f"""Generate an executive summary of this knowledge graph.

Entity types: {json.dumps(labels, indent=2)}
Relationship types: {json.dumps(rel_types, indent=2)}
Top entities by connectivity: {json.dumps(top_nodes, indent=2)}
Sample relationships: {json.dumps(sample_rels[:25], indent=2)}

Return JSON:
{{
  "executive_summary": "3-5 sentence high-level overview",
  "key_themes": ["theme1", "theme2", ...],
  "central_entities": [{{"name": "...", "role": "why this entity matters"}}],
  "notable_patterns": ["pattern1", "pattern2"],
  "knowledge_domains": ["domain1", "domain2"]
}}

Return ONLY JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        result = json.loads(text)
        result["stats"] = {
            "entity_types": len(labels),
            "relationship_types": len(rel_types),
            "total_nodes": sum(l["count"] for l in labels),
            "total_relationships": sum(r["count"] for r in rel_types),
        }
        return result
    except json.JSONDecodeError:
        return {"executive_summary": text[:500], "key_themes": [], "central_entities": [], "notable_patterns": [], "knowledge_domains": []}


def summarize_subgraph(entity_name: str, depth: int = 2) -> dict:
    nodes = neo4j_client.run_query(
        "MATCH path = (n)-[*1.." + str(min(depth, 3)) + "]-(m) "
        "WHERE toLower(n.name) CONTAINS toLower($name) "
        "UNWIND nodes(path) AS node "
        "RETURN DISTINCT node.name AS name, labels(node)[0] AS label",
        {"name": entity_name},
    )
    rels = neo4j_client.run_query(
        "MATCH (n)-[r*1.." + str(min(depth, 3)) + "]-(m) "
        "WHERE toLower(n.name) CONTAINS toLower($name) "
        "UNWIND r AS rel "
        "WITH startNode(rel) AS a, rel, endNode(rel) AS b "
        "RETURN DISTINCT a.name AS from, type(rel) AS type, b.name AS to",
        {"name": entity_name},
    )

    prompt = f"""Summarize this subgraph centered on "{entity_name}".

Entities ({len(nodes)}): {json.dumps(nodes[:30], indent=2)}
Relationships ({len(rels)}): {json.dumps(rels[:30], indent=2)}

Return JSON:
{{
  "summary": "2-3 sentence description of this entity's neighborhood",
  "key_connections": [{{"entity": "...", "relationship": "...", "significance": "..."}}],
  "insights": ["insight1", "insight2"]
}}

Return ONLY JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        result = json.loads(text)
        result["entity"] = entity_name
        result["node_count"] = len(nodes)
        result["relationship_count"] = len(rels)
        return result
    except json.JSONDecodeError:
        return {"entity": entity_name, "summary": text[:500], "key_connections": [], "insights": []}
