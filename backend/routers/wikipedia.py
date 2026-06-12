from fastapi import APIRouter, HTTPException
from backend.services.wikipedia_enricher import search_wikipedia, get_wikipedia_summary, enrich_entity

router = APIRouter(prefix="/api/wikipedia", tags=["Wikipedia Enrichment"])


@router.get("/search")
async def search_wiki(q: str, limit: int = 5):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    try:
        results = search_wikipedia(q, limit)
        return {"query": q, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{title}")
async def get_summary(title: str):
    try:
        return get_wikipedia_summary(title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrich/{entity_name}")
async def enrich(entity_name: str):
    try:
        return enrich_entity(entity_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
