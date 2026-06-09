import json
import spacy
from anthropic import Anthropic

from backend.config import ANTHROPIC_API_KEY
from backend.models.schemas import TextChunk, ExtractedEntity

nlp = spacy.load("en_core_web_sm")
client = Anthropic(api_key=ANTHROPIC_API_KEY)

SPACY_TO_SCHEMA = {
    "PERSON": "Person",
    "ORG": "Organization",
    "GPE": "Location",
    "LOC": "Location",
    "DATE": "Event",
    "PRODUCT": "Product",
    "EVENT": "Event",
    "WORK_OF_ART": "Product",
    "FAC": "Location",
    "NORP": "Organization",
}


def _spacy_extract(text: str) -> list[dict]:
    doc = nlp(text)
    entities = []
    seen = set()
    for ent in doc.ents:
        if ent.label_ in SPACY_TO_SCHEMA and ent.text.strip() not in seen:
            seen.add(ent.text.strip())
            entities.append({
                "text": ent.text.strip(),
                "label": ent.label_,
                "mapped_label": SPACY_TO_SCHEMA[ent.label_],
            })
    return entities


def _build_entity_prompt(chunk_text: str, spacy_entities: list[dict], schema: dict) -> str:
    entity_types = "\n".join(
        f"- {et['label']}: properties = {et['properties']}"
        for et in schema.get("entity_types", [])
    )

    spacy_hints = ""
    if spacy_entities:
        hints = "\n".join(
            f"  - \"{e['text']}\" (detected as {e['label']} -> likely {e['mapped_label']})"
            for e in spacy_entities
        )
        spacy_hints = f"\nPre-detected entities (NER hints — refine, reclassify, or discard as needed):\n{hints}"

    return f"""Extract all entities from the following text and classify them according to the schema below.

ENTITY TYPES:
{entity_types}

RULES:
1. Use canonical names: "Anthropic" not "anthropic" or "Anthropic Inc."
2. Assign the most specific label from the schema. If unsure, use the closest match.
3. Fill in as many properties as you can infer from the text.
4. List all text mentions/variations of each entity in the "mentions" field.
5. Set confidence to "high" if explicitly stated, "medium" if inferred, "low" if uncertain.
6. Resolve ambiguity using context: "Apple" in a tech article = Organization.
7. Do NOT extract generic/vague references like "the company" as separate entities.
8. Extract technologies, concepts, and products even if not detected by NER.
{spacy_hints}

TEXT:
{chunk_text}

Return ONLY a JSON array of objects with this exact structure:
[
  {{
    "name": "Entity Name",
    "label": "SchemaLabel",
    "properties": {{"key": "value"}},
    "mentions": ["variation1", "variation2"],
    "confidence": "high|medium|low"
  }}
]

Return ONLY valid JSON. No markdown, no explanation."""


def extract_entities(
    chunk: TextChunk, schema: dict
) -> list[ExtractedEntity]:
    spacy_entities = _spacy_extract(chunk.text)
    prompt = _build_entity_prompt(chunk.text, spacy_entities, schema)

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
        return _fallback_to_spacy(spacy_entities, chunk.chunk_index)

    spacy_names = {e["text"].lower() for e in spacy_entities}
    entities = []
    for item in parsed:
        method = "claude"
        if item.get("name", "").lower() in spacy_names:
            method = "both"

        entities.append(
            ExtractedEntity(
                name=item.get("name", ""),
                label=item.get("label", "Concept"),
                properties=item.get("properties", {}),
                mentions=item.get("mentions", [item.get("name", "")]),
                source_chunk=chunk.chunk_index,
                confidence=item.get("confidence", "medium"),
                extraction_method=method,
            )
        )

    return entities


def _fallback_to_spacy(
    spacy_entities: list[dict], chunk_index: int
) -> list[ExtractedEntity]:
    return [
        ExtractedEntity(
            name=e["text"],
            label=e["mapped_label"],
            properties={},
            mentions=[e["text"]],
            source_chunk=chunk_index,
            confidence="low",
            extraction_method="spacy",
        )
        for e in spacy_entities
    ]
