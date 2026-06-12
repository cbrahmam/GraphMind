from fastapi import APIRouter, HTTPException
from backend.services.influence_propagation import calculate_influence, find_most_influential

router = APIRouter(prefix="/api/influence", tags=["Influence Propagation"])


@router.get("/entity/{entity_name}")
async def get_entity_influence(entity_name: str, depth: int = 3):
    try:
        return calculate_influence(entity_name, max_depth=min(depth, 5))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top")
async def get_top_influential(limit: int = 10):
    try:
        return {"entities": find_most_influential(top_n=min(limit, 25))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
