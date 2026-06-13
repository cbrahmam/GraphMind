from fastapi import APIRouter, HTTPException
from backend.services.shortest_path import find_shortest_path, find_all_paths

router = APIRouter(prefix="/api/pathfinder", tags=["Path Finder"])


@router.get("/shortest")
async def shortest_path(from_entity: str, to_entity: str, max_depth: int = 10):
    if not from_entity or not to_entity:
        raise HTTPException(status_code=400, detail="from_entity and to_entity are required")
    try:
        return find_shortest_path(from_entity, to_entity, max_depth=min(max_depth, 15))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def all_paths(from_entity: str, to_entity: str, max_depth: int = 5, limit: int = 10):
    if not from_entity or not to_entity:
        raise HTTPException(status_code=400, detail="from_entity and to_entity are required")
    try:
        return find_all_paths(from_entity, to_entity, max_depth=min(max_depth, 6), limit=min(limit, 20))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
