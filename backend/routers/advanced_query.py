import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.services.conversation_memory import (
    resolve_references,
    add_turn,
    get_session,
    clear_session,
    list_sessions,
)
from backend.services.graph_rag import rag_query
from backend.services.query_templates import (
    get_templates,
    get_template,
    save_template,
    delete_template,
)
from backend.services.cypher_generator import natural_language_to_cypher
from backend.services.query_executor import execute_and_format
from backend.services.answer_generator import generate_answer
from backend.database import insert_query_history

router = APIRouter(prefix="/api/query", tags=["advanced-query"])


@router.post("/conversational")
async def conversational_query(
    question: str,
    session_id: str = "default",
):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    resolved = resolve_references(session_id, question)

    cypher_query = natural_language_to_cypher(resolved)
    if not cypher_query.cypher:
        raise HTTPException(status_code=400, detail="Could not generate query")

    query_result = execute_and_format(cypher_query)

    try:
        answer = generate_answer(query_result)
        query_result.formatted_answer = answer
    except Exception:
        query_result.formatted_answer = f"Found {query_result.result_count} results."

    add_turn(session_id, question, query_result.formatted_answer, cypher_query.cypher)

    try:
        insert_query_history({
            "id": str(uuid.uuid4()),
            "question": question,
            "cypher": cypher_query.cypher,
            "result_count": query_result.result_count,
            "execution_time_ms": query_result.execution_time_ms,
            "queried_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass

    return {
        "session_id": session_id,
        "original_question": question,
        "resolved_question": resolved,
        "result": query_result.model_dump(),
    }


@router.get("/sessions")
async def list_query_sessions():
    return {"sessions": list_sessions()}


@router.get("/session/{session_id}")
async def get_session_history(session_id: str):
    return {"session_id": session_id, "turns": get_session(session_id)}


@router.delete("/session/{session_id}")
async def clear_query_session(session_id: str):
    clear_session(session_id)
    return {"message": f"Session '{session_id}' cleared"}


@router.post("/rag")
async def graph_rag_query(question: str):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        return rag_query(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")


@router.get("/templates")
async def list_templates():
    return get_templates()


@router.get("/templates/{template_id}")
async def get_single_template(template_id: str):
    t = get_template(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return t


@router.post("/templates")
async def create_template(template: dict):
    if "id" not in template:
        template["id"] = str(uuid.uuid4())
    if "cypher" not in template:
        raise HTTPException(status_code=400, detail="Template must include 'cypher'")
    return save_template(template)


@router.delete("/templates/{template_id}")
async def remove_template(template_id: str):
    if delete_template(template_id):
        return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Template not found (or is built-in)")


@router.post("/templates/{template_id}/run")
async def run_template(template_id: str, parameters: dict = {}):
    t = get_template(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    merged_params = {**t.get("parameters", {}), **parameters}
    from backend.models.schemas import CypherQuery
    query = CypherQuery(
        cypher=t["cypher"],
        explanation=t.get("description", ""),
        query_type="search",
        parameters=merged_params,
        confidence="high",
    )
    result = execute_and_format(query)
    return result.model_dump()
