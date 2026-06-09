import json

from anthropic import Anthropic

from backend.config import ANTHROPIC_API_KEY
from backend.models.schemas import CypherQuery
from backend.neo4j_client import neo4j_client

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _get_graph_context() -> dict:
    schema = neo4j_client.get_schema()

    sample_nodes = {}
    for label_info in schema.get("node_labels", []):
        label = label_info["label"]
        samples = neo4j_client.run_query(
            f"MATCH (n:{label}) RETURN n.name AS name, n.id AS id LIMIT 5"
        )
        sample_nodes[label] = [s["name"] for s in samples if s.get("name")]

    rel_patterns = []
    for rt in schema.get("relationship_types", []):
        patterns = neo4j_client.run_query(
            f"MATCH (a)-[r:{rt['type']}]->(b) "
            "RETURN labels(a)[0] AS from_label, labels(b)[0] AS to_label "
            "LIMIT 1"
        )
        if patterns:
            rel_patterns.append({
                "type": rt["type"],
                "from_label": patterns[0]["from_label"],
                "to_label": patterns[0]["to_label"],
                "count": rt["count"],
            })

    return {
        "node_labels": schema.get("node_labels", []),
        "relationship_types": rel_patterns,
        "sample_nodes": sample_nodes,
    }


def _build_cypher_prompt(question: str, graph_context: dict) -> str:
    labels_section = ""
    for lbl in graph_context["node_labels"]:
        labels_section += f"  - :{lbl['label']} ({lbl['count']} nodes) — properties: {', '.join(lbl['property_keys'])}\n"

    rels_section = ""
    for rel in graph_context["relationship_types"]:
        rels_section += f"  - (:{rel['from_label']})-[:{rel['type']}]->(:{rel['to_label']}) — {rel['count']} relationships\n"

    samples_section = ""
    for label, names in graph_context["sample_nodes"].items():
        if names:
            samples_section += f"  {label}: {', '.join(names[:5])}\n"

    return f"""You are a Cypher query expert for Neo4j. Translate the user's natural language question into a Cypher query.

## Graph Schema

### Node Labels:
{labels_section}

### Relationship Types:
{rels_section}

### Sample Data:
{samples_section}

## Rules:
1. Use parameterized queries with $param syntax for safety — never string interpolation
2. Use OPTIONAL MATCH where appropriate to avoid missing results
3. Always include LIMIT (default 25) unless the user asks for all results
4. Return meaningful property names, not raw node objects
5. For name matching, use fuzzy matching: WHERE toLower(n.name) CONTAINS toLower($search)
6. Use shortestPath for "how connected" / "path between" questions
7. For aggregation queries, use ORDER BY and meaningful aliases
8. Return ONLY valid Neo4j Cypher — no explanatory text in the query itself

## User Question:
{question}

## Response Format:
Return a JSON object with these fields:
{{
  "cypher": "the Cypher query with $param placeholders",
  "explanation": "plain English explanation of what the query does",
  "query_type": "search|path|aggregation|pattern|recommendation",
  "parameters": {{"param_name": "value"}},
  "confidence": "high|medium|low"
}}

Return ONLY the JSON object, no other text."""


def natural_language_to_cypher(question: str) -> CypherQuery:
    graph_context = _get_graph_context()

    if not graph_context["node_labels"]:
        return CypherQuery(
            cypher="MATCH (n) RETURN n.name, labels(n) AS labels LIMIT 25",
            explanation="Graph is empty. Showing all nodes.",
            query_type="search",
            parameters={},
            confidence="low",
        )

    prompt = _build_cypher_prompt(question, graph_context)

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
        data = json.loads(text)
        return CypherQuery(
            cypher=data.get("cypher", ""),
            explanation=data.get("explanation", ""),
            query_type=data.get("query_type", "search"),
            parameters=data.get("parameters", {}),
            confidence=data.get("confidence", "medium"),
        )
    except (json.JSONDecodeError, KeyError):
        return CypherQuery(
            cypher=text if text.upper().startswith("MATCH") else "",
            explanation="Failed to parse structured response",
            query_type="search",
            parameters={},
            confidence="low",
        )


def generate_path_query(from_entity: str, to_entity: str, max_depth: int = 5) -> CypherQuery:
    cypher = (
        "MATCH (a), (b) "
        "WHERE toLower(a.name) CONTAINS toLower($from_name) "
        "AND toLower(b.name) CONTAINS toLower($to_name) "
        f"MATCH path = shortestPath((a)-[*..{min(max_depth, 10)}]-(b)) "
        "RETURN path, "
        "[n IN nodes(path) | {name: n.name, labels: labels(n)}] AS node_list, "
        "[r IN relationships(path) | {type: type(r), from: startNode(r).name, to: endNode(r).name}] AS rel_list"
    )

    return CypherQuery(
        cypher=cypher,
        explanation=f"Finding shortest path between '{from_entity}' and '{to_entity}' (max depth {max_depth})",
        query_type="path",
        parameters={"from_name": from_entity, "to_name": to_entity},
        confidence="high",
    )


def suggest_queries(limit: int = 5) -> list[str]:
    graph_context = _get_graph_context()

    if not graph_context["node_labels"]:
        return ["Upload a document to start building your knowledge graph."]

    suggestions = []

    labels = [l["label"] for l in graph_context["node_labels"]]
    samples = graph_context["sample_nodes"]

    if "Person" in labels:
        suggestions.append("Who are the most connected people in the graph?")
    if "Organization" in labels:
        suggestions.append("What organizations are in the graph?")
    if "Technology" in labels:
        suggestions.append("Which technologies are used by the most companies?")

    for label in labels[:2]:
        names = samples.get(label, [])
        if len(names) >= 2:
            suggestions.append(f"How is {names[0]} connected to {names[1]}?")

    if any(r["type"] == "FOUNDED_BY" for r in graph_context["relationship_types"]):
        suggestions.append("Who founded which companies?")
    if any(r["type"] == "WORKS_AT" for r in graph_context["relationship_types"]):
        suggestions.append("Where does everyone work?")
    if any(r["type"] == "COMPETES_WITH" for r in graph_context["relationship_types"]):
        suggestions.append("Show me all competitive relationships")

    if not suggestions:
        top_label = labels[0]
        suggestions.append(f"Show me all {top_label} nodes")
        suggestions.append("What are the most connected nodes in the graph?")

    return suggestions[:limit]
