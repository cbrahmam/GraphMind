from fastapi import APIRouter, HTTPException
from backend.services.anomaly_detector import (
    detect_contradictions,
    detect_confidence_outliers,
    detect_structural_anomalies,
    run_full_audit,
)

router = APIRouter(prefix="/api/anomaly", tags=["Anomaly Detection"])


@router.get("/contradictions")
async def get_contradictions():
    try:
        return {"contradictions": detect_contradictions()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/confidence")
async def get_confidence_outliers():
    try:
        return {"outliers": detect_confidence_outliers()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structural")
async def get_structural_anomalies():
    try:
        return {"anomalies": detect_structural_anomalies()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit")
async def get_full_audit():
    try:
        return run_full_audit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
