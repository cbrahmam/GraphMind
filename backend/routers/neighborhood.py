from fastapi import APIRouter, HTTPException
from backend.services.neighborhood_explorer import get_ego_graph

router = APIRouter(prefix="/api/neighborhood", tags=["Neighborhood Explorer"])


@router.get("/{entity_name}")
async def get_neighborhood(entity_name: str, radius: int = 2, limit: int = 100):
    try:
        result = get_ego_graph(entity_name, radius=min(radius, 4), limit=min(limit, 200))
        if not result.get("found"):
            raise HTTPException(status_code=404, detail="Entity not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
