from fastapi import APIRouter, HTTPException
from backend.services.link_predictor import (
    predict_links_common_neighbors,
    predict_links_structural,
    predict_links_ai,
)

router = APIRouter(prefix="/api/predictions", tags=["Link Prediction"])


@router.get("/common-neighbors")
async def get_common_neighbor_predictions():
    try:
        return {"predictions": predict_links_common_neighbors()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structural")
async def get_structural_predictions():
    try:
        return {"predictions": predict_links_structural()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai")
async def get_ai_predictions(limit: int = 10):
    try:
        return {"predictions": predict_links_ai(limit=min(limit, 20))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_predictions():
    try:
        common = predict_links_common_neighbors()
        structural = predict_links_structural()
        return {
            "common_neighbors": common,
            "structural": structural,
            "total": len(common) + len(structural),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
