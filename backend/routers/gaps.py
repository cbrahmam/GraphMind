from fastapi import APIRouter, HTTPException
from backend.services.knowledge_gaps import (
    find_sparse_entities,
    find_disconnected_clusters,
    find_missing_reciprocals,
    ai_gap_analysis,
)

router = APIRouter(prefix="/api/gaps", tags=["Knowledge Gaps"])


@router.get("/sparse")
async def get_sparse_entities():
    try:
        return {"gaps": find_sparse_entities()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/disconnected")
async def get_disconnected():
    try:
        return {"gaps": find_disconnected_clusters()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reciprocals")
async def get_missing_reciprocals():
    try:
        return {"gaps": find_missing_reciprocals()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis")
async def get_ai_analysis():
    try:
        return ai_gap_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
