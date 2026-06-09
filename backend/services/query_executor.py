import time

from backend.models.schemas import CypherQuery, QueryResult
from backend.neo4j_client import neo4j_client


def execute_and_format(cypher_query: CypherQuery) -> QueryResult:
    start = time.time()

    try:
        raw_results = neo4j_client.run_query(
            cypher_query.cypher, cypher_query.parameters
        )
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        return QueryResult(
            query=cypher_query,
            results=[],
            result_count=0,
            formatted_answer=f"Query execution error: {e}",
            execution_time_ms=elapsed,
        )

    elapsed = int((time.time() - start) * 1000)

    cleaned_results = _clean_results(raw_results)
    viz_data = _extract_visualization_data(raw_results, cypher_query.query_type)

    return QueryResult(
        query=cypher_query,
        results=cleaned_results,
        result_count=len(cleaned_results),
        formatted_answer="",
        visualization_data=viz_data,
        execution_time_ms=elapsed,
    )


def execute_raw_cypher(cypher: str, parameters: dict | None = None) -> QueryResult:
    query = CypherQuery(
        cypher=cypher,
        explanation="User-provided Cypher query",
        query_type="search",
        parameters=parameters or {},
        confidence="high",
    )
    return execute_and_format(query)


def _clean_results(raw_results: list[dict]) -> list[dict]:
    cleaned = []
    for record in raw_results:
        clean_record = {}
        for key, value in record.items():
            if hasattr(value, "items"):
                clean_record[key] = {
                    k: v for k, v in value.items()
                    if not k.startswith("_") and k != "id"
                }
            elif isinstance(value, list) and value and hasattr(value[0], "items"):
                clean_record[key] = [
                    {k: v for k, v in item.items() if not k.startswith("_")}
                    if hasattr(item, "items") else item
                    for item in value
                ]
            else:
                clean_record[key] = value
        cleaned.append(clean_record)
    return cleaned


def _extract_visualization_data(
    raw_results: list[dict], query_type: str
) -> dict | None:
    if query_type not in ("path", "pattern", "search"):
        return None

    nodes = {}
    links = []

    for record in raw_results:
        for key, value in record.items():
            if key == "path":
                continue

            if key == "node_list" and isinstance(value, list):
                for node_data in value:
                    if isinstance(node_data, dict) and "name" in node_data:
                        name = node_data["name"]
                        if name not in nodes:
                            nodes[name] = {
                                "id": name,
                                "name": name,
                                "label": node_data.get("labels", [""])[0]
                                if node_data.get("labels") else "",
                            }

            if key == "rel_list" and isinstance(value, list):
                for rel_data in value:
                    if isinstance(rel_data, dict):
                        links.append({
                            "source": rel_data.get("from", ""),
                            "target": rel_data.get("to", ""),
                            "type": rel_data.get("type", ""),
                        })

            if hasattr(value, "items"):
                props = dict(value)
                name = props.get("name", "")
                if name and name not in nodes:
                    nodes[name] = {
                        "id": name,
                        "name": name,
                        "label": props.get("_label", ""),
                    }

    if not nodes:
        return None

    return {"nodes": list(nodes.values()), "links": links}
