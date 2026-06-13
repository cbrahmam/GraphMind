import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def test_connection(entity_a: str, entity_b: str, via_entity: str | None = None) -> dict:
    if via_entity:
        paths = neo4j_client.run_query(
            "MATCH path = (a)-[*1..4]-(c)-[*1..4]-(b) "
            "WHERE toLower(a.name) CONTAINS toLower($a) "
            "AND toLower(b.name) CONTAINS toLower($b) "
            "AND toLower(c.name) CONTAINS toLower($via) "
            "RETURN [n IN nodes(path) | n.name] AS nodes, "
            "[r IN relationships(path) | type(r)] AS rels, length(path) AS depth "
            "LIMIT 3",
            {"a": entity_a, "b": entity_b, "via": via_entity},
        )
    else:
        paths = neo4j_client.run_query(
            "MATCH path = shortestPath((a)-[*1..6]-(b)) "
            "WHERE toLower(a.name) CONTAINS toLower($a) "
            "AND toLower(b.name) CONTAINS toLower($b) "
            "RETURN [n IN nodes(path) | n.name] AS nodes, "
            "[r IN relationships(path) | type(r)] AS rels, length(path) AS depth "
            "LIMIT 5",
            {"a": entity_a, "b": entity_b},
        )

    direct = neo4j_client.run_query(
        "MATCH (a)-[r]-(b) "
        "WHERE toLower(a.name) CONTAINS toLower($a) "
        "AND toLower(b.name) CONTAINS toLower($b) "
        "RETURN type(r) AS type",
        {"a": entity_a, "b": entity_b},
    )

    common = neo4j_client.run_query(
        "MATCH (a)-[]-(c)-[]-(b) "
        "WHERE toLower(a.name) CONTAINS toLower($a) "
        "AND toLower(b.name) CONTAINS toLower($b) "
        "AND a <> b AND a <> c AND b <> c "
        "RETURN DISTINCT c.name AS name, labels(c)[0] AS label "
        "LIMIT 10",
        {"a": entity_a, "b": entity_b},
    )

    connected = len(paths) > 0
    direct_connection = len(direct) > 0
    shortest = min((p["depth"] for p in paths), default=0) if paths else 0

    if direct_connection:
        confidence = 1.0
    elif connected and shortest <= 2:
        confidence = 0.8
    elif connected and shortest <= 4:
        confidence = 0.5
    elif connected:
        confidence = 0.3
    else:
        confidence = 0.0

    hypothesis = f"'{entity_a}' is connected to '{entity_b}'"
    if via_entity:
        hypothesis += f" through '{via_entity}'"

    return {
        "hypothesis": hypothesis,
        "result": "confirmed" if connected else "not_confirmed",
        "confidence": confidence,
        "direct_connection": direct_connection,
        "direct_relationships": [d["type"] for d in direct],
        "shortest_path_length": shortest,
        "paths_found": len(paths),
        "paths": [{"nodes": p["nodes"], "relationships": p["rels"]} for p in paths[:3]],
        "common_connections": common[:5],
        "via_entity": via_entity,
    }


def test_hypothesis_nl(question: str) -> dict:
    graph_context = neo4j_client.run_query(
        "MATCH (n)-[r]->(m) "
        "RETURN n.name AS from, type(r) AS type, m.name AS to "
        "LIMIT 50"
    )

    prompt = f"""Given this knowledge graph data, evaluate this hypothesis/question:

Question: {question}

Graph relationships (sample):
{json.dumps(graph_context[:30], indent=2)}

Return JSON:
{{
  "answer": "yes/no/partially/insufficient_data",
  "confidence": 0.0-1.0,
  "evidence_for": ["supporting evidence from the graph"],
  "evidence_against": ["contradicting evidence"],
  "explanation": "2-3 sentence analysis"
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
        result["question"] = question
        return result
    except json.JSONDecodeError:
        return {"question": question, "answer": "error", "confidence": 0, "explanation": text[:300]}
