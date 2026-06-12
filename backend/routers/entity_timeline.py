from fastapi import APIRouter, HTTPException
from backend.services.entity_timeline import build_timeline

router = APIRouter(prefix="/api/timeline/entity", tags=["Entity Timeline"])


@router.get("/{entity_name}")
async def get_entity_timeline(entity_name: str):
    try:
        result = build_timeline(entity_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
