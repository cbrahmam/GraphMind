from fastapi import APIRouter, HTTPException
from backend.services.entity_disambiguator import find_ambiguous_entities, disambiguate_entity

router = APIRouter(prefix="/api/disambiguate", tags=["Entity Disambiguation"])


@router.get("/ambiguous")
async def get_ambiguous():
    try:
        return {"entities": find_ambiguous_entities()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{entity_name}")
async def analyze_entity(entity_name: str):
    try:
        return disambiguate_entity(entity_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
