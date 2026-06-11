from fastapi import APIRouter, HTTPException

from backend.services.auth import (
    create_user,
    authenticate,
    validate_token,
    revoke_token,
    list_users,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(username: str, password: str, role: str = "viewer"):
    try:
        return create_user(username, password, role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(username: str, password: str):
    result = authenticate(username, password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result


@router.post("/logout")
async def logout(token: str):
    revoke_token(token)
    return {"message": "Logged out"}


@router.get("/me")
async def me(token: str):
    user = validate_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.get("/users")
async def users():
    return list_users()
