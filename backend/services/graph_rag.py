import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY
from backend.neo4j_client import neo4j_client
from backend.services.cypher_generator import natural_language_to_cypher
from backend.services.query_executor import execute_and_format

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _extract_entities_from_question(question: str) -> list[str]:
    words = question.replace("?", "").replace(",", "").split()
    capitalized = [w for w in words if w[0:1].isupper() and len(w) > 1 and w.lower() not in {
        "who", "what", "where", "when", "how", "why", "which", "the", "are",
        "is", "was", "were", "has", "have", "does", "did", "can", "could",
        "show", "find", "tell", "list", "get", "give",
    }]

    merged = []
    i = 0
    while i < len(capitalized):
        name = capitalized[i]
        while i + 1 < len(capitalized) and _adjacent_in(words, capitalized[i], capitalized[i+1]):
            i += 1
            name += " " + capitalized[i]
        merged.append(name)
        i += 1
    return merged


def _adjacent_in(words, a, b):
    try:
        idx_a = words.index(a)
        idx_b = words.index(b, idx_a + 1)
        return idx_b - idx_a <= 2
    except ValueError:
        return False


def _get_subgraph_context(entity_names: list[str], depth: int = 2) -> dict:
    nodes = {}
    relationships = []

    for name in entity_names:
        results = neo4j_client.run_query(
            "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
            f"OPTIONAL MATCH path = (n)-[*1..{min(depth, 3)}]-(m) "
            "RETURN n, labels(n) AS n_labels, "
            "CASE WHEN path IS NOT NULL THEN [r IN relationships(path) | "
            "{type: type(r), from: startNode(r).name, to: endNode(r).name}] "
            "ELSE [] END AS rels, "
            "CASE WHEN path IS NOT NULL THEN [nd IN nodes(path) | "
            "{name: nd.name, labels: labels(nd), source: nd._source}] "
            "ELSE [] END AS path_nodes",
            {"name": name},
        )

        for record in results:
            n = record.get("n", {})
            if n.get("name"):
                nodes[n["name"]] = {
                    "name": n["name"],
                    "labels": record.get("n_labels", []),
                    "source": n.get("_source", ""),
                }

            for pn in record.get("path_nodes", []):
                if pn.get("name") and pn["name"] not in nodes:
                    nodes[pn["name"]] = pn

            for rel in record.get("rels", []):
                rel_key = f"{rel['from']}-{rel['type']}-{rel['to']}"
                if rel_key not in {f"{r['from']}-{r['type']}-{r['to']}" for r in relationships}:
                    relationships.append(rel)

    return {"nodes": list(nodes.values()), "relationships": relationships}


def _get_source_text_snippets(entity_names: list[str]) -> list[str]:
    snippets = []
    for name in entity_names[:5]:
        results = neo4j_client.run_query(
            "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) "
            "RETURN n._source AS source, n.name AS name, n._label AS label, "
            "n._aliases AS aliases LIMIT 3",
            {"name": name},
        )
        for r in results:
            parts = [f"{r['name']} ({r.get('label', '')})"]
            if r.get('source'):
                parts.append(f"from: {r['source']}")
            if r.get('aliases'):
                parts.append(f"aliases: {r['aliases']}")
            snippets.append(", ".join(parts))
    return snippets


def rag_query(question: str) -> dict:
    entities = _extract_entities_from_question(question)

    cypher_query = natural_language_to_cypher(question)
    query_result = execute_and_format(cypher_query)

    subgraph = _get_subgraph_context(entities) if entities else {"nodes": [], "relationships": []}
    source_snippets = _get_source_text_snippets(entities) if entities else []

    context_parts = []

    if query_result.results:
        context_parts.append(f"## Cypher Query Results\n{json.dumps(query_result.results[:15], indent=2, default=str)}")

    if subgraph["nodes"]:
        context_parts.append(f"## Graph Context ({len(subgraph['nodes'])} related entities)\n" +
            "\n".join(f"- {n['name']} ({', '.join(n.get('labels', []))})" for n in subgraph["nodes"][:20]))

    if subgraph["relationships"]:
        context_parts.append("## Relationships\n" +
            "\n".join(f"- {r['from']} --[{r['type']}]--> {r['to']}" for r in subgraph["relationships"][:20]))

    if source_snippets:
        context_parts.append("## Source Information\n" + "\n".join(f"- {s}" for s in source_snippets))

    context = "\n\n".join(context_parts) if context_parts else "No graph data found for this query."

    prompt = f"""You are an AI assistant answering questions using a knowledge graph. Use the graph context below to provide a comprehensive, accurate answer.

{context}

Question: {question}

Instructions:
- Answer based on the graph data provided
- Reference specific entities and relationships
- Note connections or patterns you observe
- If the data is insufficient, say what's missing
- Be specific and cite the graph evidence"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.content[0].text.strip()

    return {
        "question": question,
        "answer": answer,
        "entities_found": entities,
        "graph_context": {
            "nodes_used": len(subgraph["nodes"]),
            "relationships_used": len(subgraph["relationships"]),
        },
        "cypher_query": cypher_query.model_dump(),
        "query_results_count": query_result.result_count,
        "sources": source_snippets,
    }
