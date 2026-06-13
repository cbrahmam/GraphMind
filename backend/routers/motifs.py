from fastapi import APIRouter, HTTPException
from backend.services.motif_detector import find_triangles, find_star_patterns, find_chains, find_all_motifs

router = APIRouter(prefix="/api/motifs", tags=["Motif Detection"])


@router.get("/triangles")
async def get_triangles(limit: int = 20):
    try:
        return {"motifs": find_triangles(min(limit, 50))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stars")
async def get_stars(min_degree: int = 5, limit: int = 15):
    try:
        return {"motifs": find_star_patterns(min_degree, min(limit, 30))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chains")
async def get_chains(min_length: int = 4, limit: int = 10):
    try:
        return {"motifs": find_chains(min_length, min(limit, 20))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all():
    try:
        return find_all_motifs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
