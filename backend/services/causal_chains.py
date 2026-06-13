import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)

CAUSAL_REL_TYPES = [
    "CAUSED_BY", "LEADS_TO", "RESULTS_IN", "ENABLES", "TRIGGERS",
    "INFLUENCES", "DEPENDS_ON", "PRECEDED_BY", "FOLLOWED_BY",
]


def find_causal_paths(from_entity: str, to_entity: str, max_depth: int = 5) -> dict:
    paths = neo4j_client.run_query(
        "MATCH path = shortestPath((a)-[*1.." + str(min(max_depth, 6)) + "]-(b)) "
        "WHERE toLower(a.name) CONTAINS toLower($from) "
        "AND toLower(b.name) CONTAINS toLower($to) "
        "RETURN [n IN nodes(path) | n.name] AS nodes, "
        "[r IN relationships(path) | type(r)] AS rels, length(path) AS depth "
        "LIMIT 5",
        {"from": from_entity, "to": to_entity},
    )

    if not paths:
        return {"from": from_entity, "to": to_entity, "chains": [], "narrative": "No path found."}

    chains = []
    for p in paths:
        chain = []
        for i, node in enumerate(p["nodes"]):
            chain.append({"entity": node})
            if i < len(p["rels"]):
                chain.append({"relationship": p["rels"][i]})
        chains.append({"steps": chain, "depth": p["depth"]})

    path_desc = []
    for p in paths[:3]:
        parts = []
        for i, node in enumerate(p["nodes"]):
            parts.append(node)
            if i < len(p["rels"]):
                parts.append(f"-[{p['rels'][i]}]->")
        path_desc.append(" ".join(parts))

    prompt = f"""Analyze these causal/connection paths between "{from_entity}" and "{to_entity}":

{chr(10).join(path_desc)}

Explain the cause-effect or influence chain. Return JSON:
{{
  "narrative": "2-3 sentence explanation of how these entities are connected",
  "causal_strength": "strong/moderate/weak/indirect",
  "key_intermediaries": ["entities that bridge the connection"]
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
        analysis = json.loads(text)
    except json.JSONDecodeError:
        analysis = {"narrative": text[:300], "causal_strength": "unknown", "key_intermediaries": []}

    return {
        "from": from_entity,
        "to": to_entity,
        "chains": chains,
        **analysis,
    }


def discover_causal_chains(max_chains: int = 10) -> list[dict]:
    candidates = neo4j_client.run_query(
        "MATCH (a)-[r]->(b)-[s]->(c) "
        "WHERE a <> c AND NOT (a)-[]->(c) "
        "RETURN DISTINCT a.name AS start, type(r) AS r1, b.name AS mid, "
        "type(s) AS r2, c.name AS end "
        "LIMIT $limit",
        {"limit": max_chains},
    )

    chains = []
    for c in candidates:
        chains.append({
            "chain": [c["start"], c["r1"], c["mid"], c["r2"], c["end"]],
            "start": c["start"],
            "intermediary": c["mid"],
            "end": c["end"],
            "path": f"{c['start']} -[{c['r1']}]-> {c['mid']} -[{c['r2']}]-> {c['end']}",
        })

    return chains
