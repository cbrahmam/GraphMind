from fastapi import APIRouter, HTTPException

from backend.services.demo_loader import get_demo_status, load_demo_data

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.get("/status")
async def demo_status():
    return get_demo_status()


@router.post("/load")
async def load_demo():
    progress = []

    def on_progress(msg):
        progress.append(msg)

    try:
        result = load_demo_data(progress_callback=on_progress)
        result["progress_log"] = progress
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo loading failed: {e}")
