import json
from anthropic import Anthropic

from backend.config import ANTHROPIC_API_KEY
from backend.models.schemas import TextChunk, ExtractedEntity, ExtractedRelationship

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _build_relationship_prompt(
    chunk_text: str, entities: list[ExtractedEntity], schema: dict
) -> str:
    entity_list = "\n".join(
        f"  - {e.name} ({e.label})" for e in entities
    )

    rel_types = "\n".join(
        f"  - {rt['type']}: {rt['from']} -> {rt['to']}"
        for rt in schema.get("relationship_types", [])
    )

    return f"""Extract all relationships between the entities listed below from the given text.

ENTITIES FOUND IN THIS TEXT:
{entity_list}

ALLOWED RELATIONSHIP TYPES:
{rel_types}

RULES:
1. Only create relationships between entities in the list above.
2. Use ONLY the relationship types listed above. If none fits, use RELATED_TO.
3. Provide the exact sentence or phrase from the text as evidence.
4. Extract implicit relationships: "Dario Amodei, CEO of Anthropic" implies WORKS_AT with role="CEO".
5. Include relationship properties where inferable (since, role, description, etc.).
6. Set confidence to "high" if explicitly stated, "medium" if inferred, "low" if uncertain.
7. A wildcard "*" in the from/to means any entity type can be used.
8. Extract ALL relationships you can find, not just the obvious ones.

TEXT:
{chunk_text}

Return ONLY a JSON array with this exact structure:
[
  {{
    "from_entity": "Entity Name",
    "from_label": "EntityLabel",
    "to_entity": "Entity Name",
    "to_label": "EntityLabel",
    "relationship_type": "RELATIONSHIP_TYPE",
    "properties": {{"key": "value"}},
    "evidence": "The exact sentence supporting this relationship",
    "confidence": "high|medium|low"
  }}
]

Return ONLY valid JSON. No markdown, no explanation."""


def extract_relationships(
    chunk: TextChunk,
    entities: list[ExtractedEntity],
    schema: dict,
) -> list[ExtractedRelationship]:
    if len(entities) < 2:
        return []

    prompt = _build_relationship_prompt(chunk.text, entities, schema)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []

    entity_names = {e.name.lower() for e in entities}
    relationships = []

    for item in parsed:
        from_name = item.get("from_entity", "")
        to_name = item.get("to_entity", "")

        if from_name.lower() not in entity_names or to_name.lower() not in entity_names:
            continue

        relationships.append(
            ExtractedRelationship(
                from_entity=from_name,
                from_label=item.get("from_label", ""),
                to_entity=to_name,
                to_label=item.get("to_label", ""),
                relationship_type=item.get("relationship_type", "RELATED_TO"),
                properties=item.get("properties", {}),
                evidence=item.get("evidence", ""),
                confidence=item.get("confidence", "medium"),
                source_chunk=chunk.chunk_index,
            )
        )

    return relationships
