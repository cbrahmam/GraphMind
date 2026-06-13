from fastapi import APIRouter, HTTPException
from backend.services.entity_comparison import compare_entities

router = APIRouter(prefix="/api/compare", tags=["Entity Comparison"])


@router.get("/")
async def compare(entity_a: str, entity_b: str):
    if not entity_a or not entity_b:
        raise HTTPException(status_code=400, detail="entity_a and entity_b are required")
    try:
        result = compare_entities(entity_a, entity_b)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
