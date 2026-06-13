from fastapi import APIRouter, HTTPException
from backend.services.data_lineage import get_entity_lineage, get_source_summary

router = APIRouter(prefix="/api/lineage", tags=["Data Lineage"])


@router.get("/entity/{entity_name}")
async def entity_lineage(entity_name: str):
    try:
        result = get_entity_lineage(entity_name)
        if not result.get("found"):
            raise HTTPException(status_code=404, detail="Entity not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
async def source_summary():
    try:
        return get_source_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
