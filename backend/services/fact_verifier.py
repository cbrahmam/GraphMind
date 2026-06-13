import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def verify_entity(entity_name: str) -> dict:
    node = neo4j_client.run_query(
        "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN n AS props, labels(n)[0] AS label LIMIT 1",
        {"name": entity_name},
    )
    if not node:
        return {"entity": entity_name, "verified": False, "reason": "Entity not found"}

    props = {k: v for k, v in dict(node[0]["props"]).items() if not k.startswith("_") and k != "id"}
    label = node[0]["label"]

    rels = neo4j_client.run_query(
        "MATCH (n)-[r]-(m) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN type(r) AS type, m.name AS related, labels(m)[0] AS related_label "
        "LIMIT 15",
        {"name": entity_name},
    )

    prompt = f"""Verify these knowledge graph facts about "{entity_name}" ({label}) using your knowledge.

Properties: {json.dumps(props, default=str)}

Relationships:
{json.dumps([{{"type": r["type"], "related": r["related"], "label": r["related_label"]}} for r in rels], indent=2)}

For each fact, determine if it's correct, incorrect, or unverifiable.

Return JSON:
{{
  "entity": "{entity_name}",
  "overall_accuracy": "high/medium/low",
  "verified_facts": [{{"fact": "description", "status": "correct/incorrect/uncertain", "note": "explanation"}}],
  "corrections": [{{"original": "wrong fact", "corrected": "correct version"}}],
  "accuracy_score": 0.0-1.0
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
        return {"entity": entity_name, "overall_accuracy": "unknown", "verified_facts": [], "accuracy_score": 0}


def verify_relationship(from_entity: str, relationship_type: str, to_entity: str) -> dict:
    prompt = f"""Verify this knowledge graph relationship:

"{from_entity}" -[{relationship_type}]-> "{to_entity}"

Is this factually correct? Return JSON:
{{
  "correct": true/false/null,
  "confidence": 0.0-1.0,
  "explanation": "brief explanation",
  "suggested_type": "correct relationship type if wrong"
}}

Return ONLY JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
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
        result["from"] = from_entity
        result["relationship"] = relationship_type
        result["to"] = to_entity
        return result
    except json.JSONDecodeError:
        return {"from": from_entity, "relationship": relationship_type, "to": to_entity, "correct": None, "confidence": 0}
