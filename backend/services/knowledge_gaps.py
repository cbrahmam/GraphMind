import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def find_sparse_entities() -> list[dict]:
    sparse = neo4j_client.run_query(
        "MATCH (n) "
        "OPTIONAL MATCH (n)-[r]-() "
        "WITH n, labels(n)[0] AS label, count(r) AS rel_count, keys(n) AS props "
        "WHERE rel_count <= 1 "
        "RETURN n.name AS name, label, rel_count, size(props) AS prop_count "
        "ORDER BY rel_count, prop_count LIMIT 30"
    )

    return [
        {
            "entity": s["name"],
            "label": s["label"],
            "relationship_count": s["rel_count"],
            "property_count": s["prop_count"],
            "gap_type": "sparse_entity",
            "suggestion": f"Entity '{s['name']}' has only {s['rel_count']} relationships and {s['prop_count']} properties",
        }
        for s in sparse
    ]


def find_disconnected_clusters() -> list[dict]:
    components = neo4j_client.run_query(
        "MATCH (n) "
        "WHERE NOT (n)-[]-() "
        "RETURN n.name AS name, labels(n)[0] AS label "
        "LIMIT 20"
    )

    return [
        {
            "entity": c["name"],
            "label": c["label"],
            "gap_type": "isolated_node",
            "suggestion": f"'{c['name']}' is completely disconnected — needs relationships",
        }
        for c in components
    ]


def find_missing_reciprocals() -> list[dict]:
    reciprocal_types = {
        "WORKS_AT": "EMPLOYS",
        "FOUNDED_BY": "FOUNDED",
        "LOCATED_IN": "CONTAINS",
        "PART_OF": "HAS_PART",
        "SUBSIDIARY_OF": "PARENT_OF",
    }

    gaps = []
    for fwd, rev in reciprocal_types.items():
        missing = neo4j_client.run_query(
            f"MATCH (a)-[r:{fwd}]->(b) "
            f"WHERE NOT (b)-[:{rev}]->(a) "
            "RETURN a.name AS from_name, b.name AS to_name "
            "LIMIT 5"
        )
        for m in missing:
            gaps.append({
                "from": m["from_name"],
                "to": m["to_name"],
                "existing_type": fwd,
                "missing_type": rev,
                "gap_type": "missing_reciprocal",
                "suggestion": f"Has [{fwd}] from {m['from_name']}→{m['to_name']} but missing [{rev}] back",
            })

    return gaps


def ai_gap_analysis() -> dict:
    labels = neo4j_client.run_query(
        "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count "
        "ORDER BY count DESC LIMIT 15"
    )
    rels = neo4j_client.run_query(
        "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count "
        "ORDER BY count DESC LIMIT 15"
    )

    sample = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) "
        "RETURN a.name AS from, labels(a)[0] AS from_label, type(r) AS type, "
        "b.name AS to, labels(b)[0] AS to_label LIMIT 30"
    )

    prompt = f"""Analyze this knowledge graph for knowledge gaps and suggest what's missing.

Entity types and counts:
{json.dumps(labels, indent=2)}

Relationship types and counts:
{json.dumps(rels, indent=2)}

Sample relationships:
{json.dumps(sample[:20], indent=2)}

Identify:
1. Entity types that are underrepresented
2. Expected relationship types that are missing
3. Areas where more data would be valuable
4. Specific entities that likely need more context

Return JSON:
{{
  "gaps": [{{"area": "...", "description": "...", "priority": "high/medium/low", "suggestion": "..."}}],
  "recommended_sources": ["data sources that could fill these gaps"],
  "completeness_score": 0.0-1.0
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
        return json.loads(text)
    except json.JSONDecodeError:
        return {"gaps": [], "recommended_sources": [], "completeness_score": 0}
