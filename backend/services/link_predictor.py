import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def predict_links_common_neighbors() -> list[dict]:
    predictions = neo4j_client.run_query(
        "MATCH (a)-[:RELATED_TO|WORKS_AT|LOCATED_IN|PART_OF]-(c)-[:RELATED_TO|WORKS_AT|LOCATED_IN|PART_OF]-(b) "
        "WHERE NOT (a)-[]-(b) AND a <> b AND id(a) < id(b) "
        "WITH a, b, count(DISTINCT c) AS common_neighbors, collect(DISTINCT c.name)[..3] AS shared "
        "WHERE common_neighbors >= 2 "
        "RETURN a.name AS entity1, labels(a)[0] AS label1, "
        "b.name AS entity2, labels(b)[0] AS label2, "
        "common_neighbors, shared "
        "ORDER BY common_neighbors DESC LIMIT 20"
    )

    return [
        {
            "entity1": p["entity1"],
            "label1": p["label1"],
            "entity2": p["entity2"],
            "label2": p["label2"],
            "score": p["common_neighbors"],
            "method": "common_neighbors",
            "shared_connections": p["shared"],
        }
        for p in predictions
    ]


def predict_links_structural() -> list[dict]:
    predictions = neo4j_client.run_query(
        "MATCH (a)-[r1]->(c)<-[r2]-(b) "
        "WHERE NOT (a)-[]-(b) AND a <> b AND id(a) < id(b) AND type(r1) = type(r2) "
        "WITH a, b, type(r1) AS shared_rel, count(DISTINCT c) AS count "
        "WHERE count >= 1 "
        "RETURN a.name AS entity1, labels(a)[0] AS label1, "
        "b.name AS entity2, labels(b)[0] AS label2, "
        "shared_rel, count "
        "ORDER BY count DESC LIMIT 15"
    )

    return [
        {
            "entity1": p["entity1"],
            "label1": p["label1"],
            "entity2": p["entity2"],
            "label2": p["label2"],
            "score": p["count"],
            "method": "structural_similarity",
            "shared_relationship_type": p["shared_rel"],
        }
        for p in predictions
    ]


def predict_links_ai(limit: int = 10) -> list[dict]:
    nodes = neo4j_client.run_query(
        "MATCH (n)-[r]-() "
        "WITH n, count(r) AS degree, labels(n)[0] AS label "
        "RETURN n.name AS name, label, degree "
        "ORDER BY degree DESC LIMIT 30"
    )
    if not nodes:
        return []

    rels = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) "
        "RETURN a.name AS from, type(r) AS type, b.name AS to "
        "LIMIT 50"
    )

    prompt = f"""Given this knowledge graph structure, predict likely missing connections.

Entities (top by connectivity):
{json.dumps([{"name": n["name"], "label": n["label"]} for n in nodes[:20]], indent=2)}

Existing relationships:
{json.dumps([{"from": r["from"], "type": r["type"], "to": r["to"]} for r in rels[:30]], indent=2)}

Predict up to {limit} missing links that likely exist in the real world but aren't in the graph.

Return a JSON array:
[{{"entity1": "name", "entity2": "name", "predicted_type": "RELATIONSHIP_TYPE", "confidence": 0.0-1.0, "reasoning": "why this link likely exists"}}]

Return ONLY the JSON array."""

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
        predictions = json.loads(text)
        for p in predictions:
            p["method"] = "ai_prediction"
        return predictions[:limit]
    except json.JSONDecodeError:
        return []
