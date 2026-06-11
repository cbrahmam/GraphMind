from fastapi import APIRouter, HTTPException

from backend.services.scheduler import (
    create_schedule,
    list_schedules,
    get_schedule,
    update_schedule,
    delete_schedule,
    check_watched_folder,
)

router = APIRouter(prefix="/api/schedules", tags=["scheduler"])


@router.get("")
async def list_all():
    return list_schedules()


@router.post("")
async def create(
    name: str,
    source_type: str,
    source_config: dict,
    interval_minutes: int = 60,
):
    return create_schedule(name, source_type, source_config, interval_minutes)


@router.get("/{schedule_id}")
async def get_one(schedule_id: str):
    s = get_schedule(schedule_id)
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return s


@router.put("/{schedule_id}")
async def update_one(schedule_id: str, updates: dict):
    s = update_schedule(schedule_id, updates)
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return s


@router.delete("/{schedule_id}")
async def delete_one(schedule_id: str):
    if delete_schedule(schedule_id):
        return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Schedule not found")


@router.get("/watch/check")
async def check_watch():
    files = check_watched_folder()
    return {"new_files": files, "count": len(files)}
