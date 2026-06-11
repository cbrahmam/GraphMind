import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def resolve_cross_document(chunk_text: str, document_context: str = "") -> list[dict]:
    existing = neo4j_client.run_query(
        "MATCH (n) RETURN n.name AS name, labels(n)[0] AS label LIMIT 200"
    )
    if not existing:
        return []

    entity_list = [f"{e['name']} ({e['label']})" for e in existing]

    prompt = f"""Given these known entities in a knowledge graph:
{chr(10).join(f'- {e}' for e in entity_list[:100])}

And this text from document "{document_context}":
---
{chunk_text[:2000]}
---

Find references in the text that refer to existing entities in the graph, including:
- Pronouns ("the company", "they", "it", "he", "she")
- Abbreviations or acronyms
- Partial names or informal references
- Descriptive references ("the AI safety startup", "the search giant")

Return a JSON array of matches:
[{{"reference": "the text reference", "resolves_to": "Entity Name", "confidence": "high|medium|low"}}]

Only include high-confidence matches. Return ONLY the JSON array."""

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
        return []


def link_coreferenced_entities(resolutions: list[dict]) -> int:
    linked = 0
    for r in resolutions:
        if r.get("confidence") not in ("high", "medium"):
            continue
        entity_name = r.get("resolves_to", "")
        if not entity_name:
            continue

        existing = neo4j_client.run_query(
            "MATCH (n) WHERE toLower(n.name) = toLower($name) RETURN n.name, n._aliases",
            {"name": entity_name},
        )
        if existing:
            current_aliases = existing[0].get("_aliases", "") or ""
            ref = r.get("reference", "")
            if ref and ref not in current_aliases:
                new_aliases = f"{current_aliases}, {ref}".strip(", ")
                neo4j_client.run_query(
                    "MATCH (n) WHERE toLower(n.name) = toLower($name) SET n._aliases = $aliases",
                    {"name": entity_name, "aliases": new_aliases},
                )
                linked += 1
    return linked
