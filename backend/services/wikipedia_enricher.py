import json
import httpx
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)

WIKI_API = "https://en.wikipedia.org/w/api.php"


def search_wikipedia(query: str, limit: int = 3) -> list[dict]:
    resp = httpx.get(WIKI_API, params={
        "action": "opensearch",
        "search": query,
        "limit": limit,
        "format": "json",
    }, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    results = []
    if len(data) >= 4:
        for title, desc, url in zip(data[1], data[2], data[3]):
            results.append({"title": title, "description": desc, "url": url})
    return results


def get_wikipedia_summary(title: str) -> dict:
    resp = httpx.get(WIKI_API, params={
        "action": "query",
        "titles": title,
        "prop": "extracts|pageimages|info",
        "exintro": True,
        "explaintext": True,
        "inprop": "url",
        "pithumbsize": 300,
        "format": "json",
    }, timeout=15)
    resp.raise_for_status()
    pages = resp.json().get("query", {}).get("pages", {})

    for page_id, page in pages.items():
        if page_id == "-1":
            return {"found": False, "title": title}
        return {
            "found": True,
            "title": page.get("title", title),
            "extract": page.get("extract", ""),
            "url": page.get("fullurl", ""),
            "thumbnail": page.get("thumbnail", {}).get("source", ""),
        }
    return {"found": False, "title": title}


def enrich_entity(entity_name: str) -> dict:
    node = neo4j_client.run_query(
        "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
        "RETURN n.name AS name, labels(n)[0] AS label LIMIT 1",
        {"name": entity_name},
    )
    if not node:
        return {"entity": entity_name, "enriched": False, "reason": "Entity not found in graph"}

    actual_name = node[0]["name"]
    label = node[0]["label"]

    results = search_wikipedia(actual_name, limit=3)
    if not results:
        return {"entity": actual_name, "enriched": False, "reason": "No Wikipedia results"}

    summary = get_wikipedia_summary(results[0]["title"])
    if not summary.get("found"):
        return {"entity": actual_name, "enriched": False, "reason": "Wikipedia page not found"}

    extract = summary["extract"][:2000]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{"role": "user", "content": f"""From this Wikipedia extract about "{actual_name}", extract key facts as structured properties.

Extract: {extract}

Return a JSON object with factual properties suitable for a knowledge graph node of type "{label}":
{{"description": "...", "founded": "year if applicable", "location": "...", "notable_for": "...", "wikipedia_url": "{summary.get('url', '')}"}}

Return ONLY JSON. Only include properties that are clearly stated."""}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        properties = json.loads(text)
    except json.JSONDecodeError:
        properties = {"description": extract[:200], "wikipedia_url": summary.get("url", "")}

    set_clauses = ", ".join(f"n.wiki_{k} = ${k}" for k in properties.keys())
    if set_clauses:
        neo4j_client.run_query(
            f"MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) SET {set_clauses}",
            {"name": entity_name, **properties},
        )

    return {
        "entity": actual_name,
        "enriched": True,
        "wikipedia_title": summary["title"],
        "wikipedia_url": summary.get("url", ""),
        "properties_added": list(properties.keys()),
    }
