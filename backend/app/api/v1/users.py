from __future__ import annotations
from fastapi import APIRouter, HTTPException, status
from app.api.deps import CurrentUser, DbDep
from app.schemas.user import UpdateMeRequest, UserResponse
from app.services import user_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )


@router.patch("/me", response_model=UserResponse)
async def update_me(req: UpdateMeRequest, current_user: CurrentUser, db: DbDep):
    try:
        user = await user_service.update_me(db, current_user, req)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.name,
        is_active=user.is_active,
        created_at=user.created_at,
    )
