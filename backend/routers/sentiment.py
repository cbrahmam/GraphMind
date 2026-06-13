from fastapi import APIRouter, HTTPException
from backend.services.sentiment_analyzer import analyze_relationship_sentiment, get_sentiment_map

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment Analysis"])


@router.get("/relationship")
async def get_sentiment(from_entity: str, to_entity: str):
    if not from_entity or not to_entity:
        raise HTTPException(status_code=400, detail="from_entity and to_entity are required")
    try:
        return analyze_relationship_sentiment(from_entity, to_entity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map")
async def get_map():
    try:
        return get_sentiment_map()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
