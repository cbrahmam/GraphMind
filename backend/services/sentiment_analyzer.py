import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)

POSITIVE_RELS = {"COLLABORATES_WITH", "SUPPORTS", "FUNDS", "PARTNERS_WITH", "ALLIES_WITH", "EMPLOYS", "FOUNDED_BY", "MEMBER_OF"}
NEGATIVE_RELS = {"COMPETES_WITH", "OPPOSES", "CONFLICTS_WITH", "SANCTIONS", "SUED_BY", "CRITICIZES"}
NEUTRAL_RELS = {"RELATED_TO", "LOCATED_IN", "PART_OF", "WORKS_AT", "HEADQUARTERED_IN"}


def analyze_relationship_sentiment(from_entity: str, to_entity: str) -> dict:
    rels = neo4j_client.run_query(
        "MATCH (a)-[r]-(b) "
        "WHERE toLower(a.name) CONTAINS toLower($a) "
        "AND toLower(b.name) CONTAINS toLower($b) "
        "RETURN type(r) AS type, properties(r) AS props, "
        "startNode(r).name = a.name AS outgoing",
        {"a": from_entity, "b": to_entity},
    )

    if not rels:
        return {"from": from_entity, "to": to_entity, "sentiment": "unknown", "relationships": []}

    rel_types = [r["type"] for r in rels]

    prompt = f"""Classify the sentiment of the relationship between "{from_entity}" and "{to_entity}" based on these relationship types: {', '.join(rel_types)}.

Return JSON:
{{
  "sentiment": "positive/negative/neutral/mixed",
  "score": -1.0 to 1.0,
  "reasoning": "brief explanation"
}}

Return ONLY JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=128,
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
        analysis = {"sentiment": "unknown", "score": 0, "reasoning": text[:100]}

    return {
        "from": from_entity,
        "to": to_entity,
        "relationship_types": rel_types,
        **analysis,
    }


def get_sentiment_map() -> dict:
    rels = neo4j_client.run_query(
        "MATCH (a)-[r]->(b) "
        "RETURN a.name AS from, type(r) AS type, b.name AS to "
        "LIMIT 100"
    )

    positive = []
    negative = []
    neutral = []

    for r in rels:
        entry = {"from": r["from"], "to": r["to"], "type": r["type"]}
        if r["type"] in POSITIVE_RELS:
            positive.append(entry)
        elif r["type"] in NEGATIVE_RELS:
            negative.append(entry)
        else:
            neutral.append(entry)

    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "summary": {
            "positive_count": len(positive),
            "negative_count": len(negative),
            "neutral_count": len(neutral),
        },
    }
