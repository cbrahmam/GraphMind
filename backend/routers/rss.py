from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.rss_ingester import add_feed, remove_feed, list_feeds, fetch_feed, fetch_and_ingest

router = APIRouter(prefix="/api/rss", tags=["RSS Feeds"])


class AddFeedRequest(BaseModel):
    url: str
    name: str = ""
    category: str = "general"


@router.get("/feeds")
async def get_feeds():
    return {"feeds": list_feeds()}


@router.post("/feeds")
async def create_feed(req: AddFeedRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        feed = add_feed(req.url, req.name, req.category)
        return feed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/feeds/{feed_id}")
async def delete_feed(feed_id: str):
    if remove_feed(feed_id):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Feed not found")


@router.post("/feeds/{feed_id}/fetch")
async def fetch_feed_articles(feed_id: str):
    try:
        result = fetch_and_ingest(feed_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview")
async def preview_feed(req: AddFeedRequest):
    try:
        articles = fetch_feed(req.url)
        return {"url": req.url, "article_count": len(articles), "articles": articles[:10]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
