from fastapi import APIRouter, HTTPException
from backend.services.graph_summarizer import summarize_full_graph, summarize_subgraph

router = APIRouter(prefix="/api/summarize", tags=["Graph Summarization"])


@router.get("/full")
async def get_full_summary():
    try:
        return summarize_full_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_name}")
async def get_entity_summary(entity_name: str, depth: int = 2):
    try:
        return summarize_subgraph(entity_name, depth=min(depth, 4))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
