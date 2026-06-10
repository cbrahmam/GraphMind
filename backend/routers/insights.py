from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.services.graph_algorithms import (
    run_centrality,
    detect_communities,
    find_similar,
)
from backend.services.insights_generator import (
    generate_graph_insights,
    get_latest_insights,
)

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/centrality")
async def centrality(
    algorithm: str = Query(default="degree"),
    label: Optional[str] = None,
):
    if algorithm not in ("degree", "pagerank", "betweenness"):
        raise HTTPException(status_code=400, detail="Algorithm must be degree, pagerank, or betweenness")
    try:
        return run_centrality(algorithm, label)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Centrality analysis failed: {e}")


@router.get("/communities")
async def communities():
    try:
        return detect_communities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Community detection failed: {e}")


@router.get("/similar/{node_name}")
async def similar(
    node_name: str,
    label: Optional[str] = None,
    top_n: int = Query(default=5, ge=1, le=20),
):
    try:
        return find_similar(node_name, label, top_n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity analysis failed: {e}")


@router.post("/generate")
async def generate():
    try:
        return generate_graph_insights()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {e}")


@router.get("/latest")
async def latest():
    insights = get_latest_insights()
    if not insights:
        raise HTTPException(status_code=404, detail="No insights generated yet. Run POST /api/insights/generate first.")
    return insights
