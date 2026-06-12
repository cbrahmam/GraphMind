import json
import re
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def build_timeline(entity_name: str) -> dict:
    node = neo4j_client.run_query(
        "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN n, labels(n) AS labels LIMIT 1",
        {"name": entity_name},
    )
    if not node:
        return {"entity": entity_name, "events": [], "narrative": "Entity not found."}

    props = dict(node[0]["n"])
    label = node[0]["labels"][0] if node[0]["labels"] else ""

    rels = neo4j_client.run_query(
        "MATCH (n)-[r]-(m) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN type(r) AS type, m.name AS related, labels(m)[0] AS related_label, "
        "properties(r) AS props, startNode(r).name = n.name AS outgoing "
        "ORDER BY r._extracted_at",
        {"name": entity_name},
    )

    context = {
        "entity": entity_name,
        "label": label,
        "properties": {k: v for k, v in props.items() if not k.startswith("_") and k != "id"},
        "relationships": [
            {"type": r["type"], "related": r["related"], "related_label": r["related_label"],
             "direction": "outgoing" if r["outgoing"] else "incoming"}
            for r in rels
        ],
    }

    prompt = f"""Build a chronological timeline for the entity "{entity_name}" ({label}) based on this knowledge graph data.

Entity properties: {json.dumps(context['properties'], default=str)}

Relationships ({len(context['relationships'])}):
{json.dumps(context['relationships'][:30], indent=2)}

Generate a JSON response:
{{
  "events": [
    {{"date": "YYYY or YYYY-MM or approximate", "event": "what happened", "related_entities": ["names"], "source": "inferred from relationship type"}}
  ],
  "narrative": "A 3-5 sentence chronological narrative of this entity's story"
}}

Order events chronologically. If dates are unknown, use approximate ordering based on relationship types (FOUNDED_BY before WORKS_AT, etc.). Return ONLY JSON."""

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
        result["entity"] = entity_name
        result["label"] = label
        return result
    except json.JSONDecodeError:
        return {
            "entity": entity_name,
            "label": label,
            "events": [],
            "narrative": text[:500],
        }
