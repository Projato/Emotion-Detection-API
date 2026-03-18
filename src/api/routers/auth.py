from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies.auth import (
    create_access_token,
    hash_password,
    verify_password,
)

from src.api.dependencies.database import get_db
from src.models.user import TokenResponse, UserLogin, UserRegister, UserResponse
from src.schemas.user import user_helper


router = APIRouter(prefix="/auth", tags=["Authentication"]) #router instance with prefix and tags for documentation grouping (Swagger)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegister,
    db = Depends(get_db),
) -> dict:
    existing_user = await db.users.find_one({"username": payload.username})

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists.",
        )

    new_user = {
        "username": payload.username,
        "hashed_password": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
    }

    result = await db.users.insert_one(new_user)
    new_user["_id"] = result.inserted_id

    return user_helper(new_user)

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: UserLogin,
    db = Depends(get_db),
) -> dict[str, str]:
    user = await db.users.find_one({"username": payload.username})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    if not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token = create_access_token({"sub": user["username"]})

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.get("/ping", status_code=status.HTTP_200_OK) #route 2: simple ping endpoint to test if the router is working
def auth_ping() -> dict[str, str]:
    return {"message": "Auth router is working."}