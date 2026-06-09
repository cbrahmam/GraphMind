import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.database import insert_query_history, list_query_history
from backend.models.schemas import (
    NLQueryRequest,
    CypherQueryRequest,
    PathRequest,
)
from backend.services.cypher_generator import (
    natural_language_to_cypher,
    generate_path_query,
    suggest_queries,
)
from backend.services.query_executor import execute_and_format, execute_raw_cypher
from backend.services.answer_generator import generate_answer, generate_path_narrative

router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("")
async def ask_question(request: NLQueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        cypher_query = natural_language_to_cypher(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate query: {e}")

    if not cypher_query.cypher:
        raise HTTPException(status_code=400, detail="Could not generate a valid Cypher query for this question")

    query_result = execute_and_format(cypher_query)

    try:
        answer = generate_answer(query_result)
        query_result.formatted_answer = answer
    except Exception:
        query_result.formatted_answer = _basic_answer(query_result)

    _save_history(request.question, cypher_query.cypher, query_result)

    return query_result.model_dump()


@router.post("/cypher")
async def run_cypher(request: CypherQueryRequest):
    if not request.cypher.strip():
        raise HTTPException(status_code=400, detail="Cypher query cannot be empty")

    forbidden = ["DELETE", "DETACH", "DROP", "CREATE INDEX", "REMOVE"]
    upper = request.cypher.upper()
    for word in forbidden:
        if word in upper and "RETURN" not in upper:
            raise HTTPException(
                status_code=400,
                detail=f"Destructive operations ({word}) are not allowed through this endpoint",
            )

    query_result = execute_raw_cypher(request.cypher, request.parameters)

    _save_history(request.cypher, request.cypher, query_result)

    return query_result.model_dump()


@router.get("/suggestions")
async def get_suggestions():
    try:
        suggestions = suggest_queries()
    except Exception:
        suggestions = [
            "Show me all nodes in the graph",
            "What are the most connected entities?",
        ]
    return {"suggestions": suggestions}


@router.get("/history")
async def get_query_history():
    return list_query_history()


@router.post("/path")
async def find_path(request: PathRequest):
    if not request.from_entity.strip() or not request.to_entity.strip():
        raise HTTPException(status_code=400, detail="Both from_entity and to_entity are required")

    cypher_query = generate_path_query(
        request.from_entity, request.to_entity, request.max_depth
    )

    query_result = execute_and_format(cypher_query)

    try:
        narrative = generate_path_narrative(query_result.results)
        query_result.formatted_answer = narrative
    except Exception:
        query_result.formatted_answer = (
            f"Found {query_result.result_count} path(s) between "
            f"'{request.from_entity}' and '{request.to_entity}'"
        )

    _save_history(
        f"Path: {request.from_entity} -> {request.to_entity}",
        cypher_query.cypher,
        query_result,
    )

    return query_result.model_dump()


def _save_history(question: str, cypher: str, result):
    try:
        insert_query_history({
            "id": str(uuid.uuid4()),
            "question": question,
            "cypher": cypher,
            "result_count": result.result_count,
            "execution_time_ms": result.execution_time_ms,
            "queried_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass


def _basic_answer(result) -> str:
    if not result.results:
        return "No results found."
    count = result.result_count
    if count == 1:
        row = result.results[0]
        parts = [f"{k}: {v}" for k, v in row.items() if v is not None]
        return "; ".join(parts) if parts else "1 result found."
    return f"Found {count} results."
