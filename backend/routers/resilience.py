from fastapi import APIRouter, HTTPException
from backend.services.network_resilience import find_critical_nodes, analyze_resilience

router = APIRouter(prefix="/api/resilience", tags=["Network Resilience"])


@router.get("/critical")
async def get_critical(top_n: int = 10):
    try:
        return {"critical_nodes": find_critical_nodes(min(top_n, 20))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis")
async def get_analysis():
    try:
        return analyze_resilience()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
