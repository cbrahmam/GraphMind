from fastapi import APIRouter, HTTPException, Query
from backend.services.audit_log import get_logs, get_log_stats

router = APIRouter(prefix="/api/audit", tags=["Audit Log"])


@router.get("/logs")
async def list_logs(
    limit: int = 100,
    action: str | None = None,
    user: str | None = None,
    resource: str | None = None,
    since: str | None = None,
):
    try:
        logs = get_logs(limit=min(limit, 500), action=action, user=user, resource=resource, since=since)
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def audit_stats():
    try:
        return get_log_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
