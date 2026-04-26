from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import DbDep, require_role
from app.models.user import User
from app.schemas.user import AdminUpdateUserRequest, UserResponse
from app.services import user_service

router = APIRouter()

AdminUser = Annotated[User, Depends(require_role("admin"))]


@router.get("/users", response_model=dict)
async def list_users(
    _: AdminUser,
    db: DbDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    users, total = await user_service.list_users(db, page, page_size)
    return {
        "items": [
            UserResponse(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role.name,
                is_active=u.is_active,
                created_at=u.created_at,
            )
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    req: AdminUpdateUserRequest,
    _: AdminUser,
    db: DbDep,
):
    try:
        user = await user_service.admin_update_user(db, user_id, req)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.name,
        is_active=user.is_active,
        created_at=user.created_at,
    )
