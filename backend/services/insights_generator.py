import json

from anthropic import Anthropic

from backend.config import ANTHROPIC_API_KEY
from backend.services.graph_algorithms import run_centrality, detect_communities, get_graph_health

client = Anthropic(api_key=ANTHROPIC_API_KEY)

_latest_insights = None


def generate_graph_insights():
    global _latest_insights

    health = get_graph_health()
    centrality = run_centrality("degree")
    communities = detect_communities()

    prompt = f"""Analyze this knowledge graph and generate insights.

## Graph Statistics
- Nodes: {health['total_nodes']}, Relationships: {health['total_relationships']}
- Avg connections per node: {health['avg_connections']}
- Density: {health['density']}
- Isolated nodes: {health['isolated_nodes']}
- Labels: {json.dumps(health['label_counts'])}
- Relationship types: {json.dumps(health['relationship_type_counts'])}

## Top Entities by Connections
{json.dumps(centrality[:10], indent=2)}

## Communities Detected ({len(communities)})
{json.dumps([{{'id': c['id'], 'name': c['suggested_name'], 'count': c['node_count'], 'dominant': c['dominant_label']}} for c in communities[:10]], indent=2)}

Generate a JSON response with:
{{
  "summary": "2-3 sentence overall description of the graph",
  "key_entities": [{{"name": "...", "why": "..."}}],
  "hidden_connections": ["non-obvious relationship descriptions"],
  "clusters_description": ["what each community represents"],
  "knowledge_gaps": ["entities or areas with sparse connections"],
  "insights": [
    {{
      "title": "short title",
      "description": "detailed finding",
      "insight_type": "pattern|anomaly|recommendation|fact",
      "related_entities": ["entity names"],
      "priority": "high|medium|low"
    }}
  ],
  "questions_to_explore": ["interesting follow-up questions"]
}}

Return ONLY JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        insights = json.loads(text)
    except json.JSONDecodeError:
        insights = {
            "summary": "Could not generate structured insights.",
            "key_entities": [{"name": c["node_name"], "why": f"Rank #{c['rank']} by connections"} for c in centrality[:5]],
            "hidden_connections": [],
            "clusters_description": [c["suggested_name"] for c in communities[:5]],
            "knowledge_gaps": [f"{health['isolated_nodes']} isolated nodes detected"],
            "insights": [],
            "questions_to_explore": [],
        }

    insights["health"] = health
    insights["centrality_data"] = centrality[:10]
    insights["community_data"] = communities

    _latest_insights = insights
    return insights


def get_latest_insights():
    return _latest_insights
