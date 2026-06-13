from fastapi import APIRouter, HTTPException
from backend.services.source_reliability import get_source_scores, get_source_detail

router = APIRouter(prefix="/api/reliability", tags=["Source Reliability"])


@router.get("/scores")
async def get_scores():
    try:
        return {"sources": get_source_scores()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/source/{source_name}")
async def get_detail(source_name: str):
    try:
        return get_source_detail(source_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
