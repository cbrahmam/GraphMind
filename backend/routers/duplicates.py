from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.duplicate_detector import find_duplicates, merge_entities, get_duplicate_stats

router = APIRouter(prefix="/api/duplicates", tags=["Duplicate Detection"])


class MergeRequest(BaseModel):
    keep_id: int
    remove_id: int


@router.get("/")
async def get_duplicates(threshold: float = 0.8):
    try:
        return {"duplicates": find_duplicates(threshold=max(0.5, min(threshold, 1.0)))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merge")
async def merge(req: MergeRequest):
    try:
        result = merge_entities(req.keep_id, req.remove_id)
        if not result.get("merged"):
            raise HTTPException(status_code=400, detail=result.get("error", "Merge failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def dup_stats():
    try:
        return get_duplicate_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
