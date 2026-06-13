from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.backup_restore import create_backup, list_backups, restore_backup, delete_backup

router = APIRouter(prefix="/api/backups", tags=["Backup & Restore"])


class CreateBackup(BaseModel):
    name: str = ""


@router.get("/")
async def get_backups():
    return {"backups": list_backups()}


@router.post("/")
async def make_backup(req: CreateBackup):
    try:
        return create_backup(req.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{backup_name}/restore")
async def do_restore(backup_name: str):
    try:
        result = restore_backup(backup_name)
        if not result.get("restored"):
            raise HTTPException(status_code=400, detail=result.get("error", "Restore failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{backup_name}")
async def remove_backup(backup_name: str):
    if delete_backup(backup_name):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Backup not found")
