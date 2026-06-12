from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.vector_store import store_embedding, search_similar, get_store_stats

router = APIRouter(prefix="/api/vectors", tags=["Vector Store"])


class StoreRequest(BaseModel):
    entity_name: str
    text: str
    label: str = ""
    source: str = ""


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/store")
async def store_vec(req: StoreRequest):
    if not req.entity_name.strip() or not req.text.strip():
        raise HTTPException(status_code=400, detail="entity_name and text are required")
    try:
        return store_embedding(req.entity_name, req.text, req.label, req.source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_vec(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    try:
        results = search_similar(req.query, top_k=min(req.top_k, 20))
        return {"query": req.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    try:
        return get_store_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
