import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def find_ambiguous_entities() -> list[dict]:
    dupes = neo4j_client.run_query(
        "MATCH (a), (b) "
        "WHERE a.name = b.name AND id(a) < id(b) "
        "RETURN a.name AS name, labels(a)[0] AS label_a, labels(b)[0] AS label_b, "
        "id(a) AS id_a, id(b) AS id_b "
        "LIMIT 20"
    )

    ambiguous = []
    for d in dupes:
        ambiguous.append({
            "name": d["name"],
            "instances": [
                {"id": d["id_a"], "label": d["label_a"]},
                {"id": d["id_b"], "label": d["label_b"]},
            ],
            "reason": "same_name_different_labels" if d["label_a"] != d["label_b"] else "exact_duplicate",
        })

    similar = neo4j_client.run_query(
        "MATCH (a), (b) "
        "WHERE id(a) < id(b) AND a.name IS NOT NULL AND b.name IS NOT NULL "
        "AND toLower(a.name) = toLower(b.name) AND a.name <> b.name "
        "RETURN a.name AS name_a, b.name AS name_b, "
        "labels(a)[0] AS label_a, labels(b)[0] AS label_b "
        "LIMIT 20"
    )

    for s in similar:
        ambiguous.append({
            "name": s["name_a"],
            "variant": s["name_b"],
            "labels": [s["label_a"], s["label_b"]],
            "reason": "case_variant",
        })

    return ambiguous


def disambiguate_entity(entity_name: str) -> dict:
    matches = neo4j_client.run_query(
        "MATCH (n) WHERE toLower(n.name) = toLower($name) "
        "OPTIONAL MATCH (n)-[r]-(m) "
        "RETURN n.name AS name, labels(n)[0] AS label, id(n) AS node_id, "
        "collect(DISTINCT {type: type(r), related: m.name, related_label: labels(m)[0]})[..5] AS context",
        {"name": entity_name},
    )

    if len(matches) <= 1:
        return {"entity": entity_name, "ambiguous": False, "matches": len(matches)}

    instances = []
    for m in matches:
        instances.append({
            "name": m["name"],
            "label": m["label"],
            "node_id": m["node_id"],
            "context": m["context"],
        })

    prompt = f"""These entities share the name "{entity_name}" in a knowledge graph. Determine if they refer to the same or different real-world entities.

Instances:
{json.dumps(instances, indent=2)}

Return JSON:
{{
  "same_entity": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "explain why they are/aren't the same",
  "recommendation": "merge/keep_separate/needs_review"
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
        analysis = json.loads(text)
    except json.JSONDecodeError:
        analysis = {"same_entity": None, "confidence": 0, "reasoning": text[:200], "recommendation": "needs_review"}

    return {
        "entity": entity_name,
        "ambiguous": True,
        "instance_count": len(instances),
        "instances": instances,
        **analysis,
    }
