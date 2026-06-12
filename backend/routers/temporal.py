from fastapi import APIRouter, HTTPException
from backend.services.temporal_graph import get_graph_at_time, get_growth_timeline, get_entity_evolution

router = APIRouter(prefix="/api/temporal", tags=["Temporal Graph"])


@router.get("/snapshot")
async def graph_snapshot(before: str):
    if not before:
        raise HTTPException(status_code=400, detail="'before' timestamp is required")
    try:
        return get_graph_at_time(before)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/growth")
async def growth_timeline(interval: str = "day"):
    try:
        timeline = get_growth_timeline(interval)
        return {"interval": interval, "timeline": timeline}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_name}")
async def entity_evolution(entity_name: str):
    try:
        evolution = get_entity_evolution(entity_name)
        return {"entity": entity_name, "evolution": evolution}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
