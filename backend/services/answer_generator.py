import json

from anthropic import Anthropic

from backend.config import ANTHROPIC_API_KEY
from backend.models.schemas import QueryResult

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def generate_answer(query_result: QueryResult) -> str:
    if not query_result.results:
        return "No results found for your query. Try rephrasing your question or check if the relevant data has been ingested."

    results_text = json.dumps(query_result.results[:20], indent=2, default=str)

    prompt = f"""You are an AI assistant answering questions about a knowledge graph.

The user asked: "{query_result.query.explanation}"

The Cypher query executed was:
{query_result.query.cypher}

Results ({query_result.result_count} total):
{results_text}

Generate a clear, natural language answer that:
1. Directly answers the question
2. References specific data from the results
3. Mentions relevant connections or patterns
4. Is concise (2-4 sentences for simple queries, more for complex ones)

If the results are empty or don't fully answer the question, say so honestly.
Return ONLY the answer text, no JSON or formatting."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()


def generate_path_narrative(path_results: list[dict]) -> str:
    if not path_results:
        return "No path found between these entities."

    record = path_results[0]
    node_list = record.get("node_list", [])
    rel_list = record.get("rel_list", [])

    if not node_list or not rel_list:
        return "A path exists but could not be described."

    steps = []
    for rel in rel_list:
        from_name = rel.get("from", "?")
        to_name = rel.get("to", "?")
        rel_type = rel.get("type", "CONNECTED_TO").replace("_", " ")
        steps.append(f"{from_name} {rel_type} {to_name}")

    narrative = " → ".join(steps)

    start = node_list[0].get("name", "?") if node_list else "?"
    end = node_list[-1].get("name", "?") if node_list else "?"

    return (
        f"Connection from {start} to {end} ({len(rel_list)} steps):\n"
        f"{narrative}"
    )
