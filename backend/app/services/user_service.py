from __future__ import annotations
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.models.user import User
from app.schemas.user import AdminUpdateUserRequest, UpdateMeRequest


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def update_me(db: AsyncSession, user: User, req: UpdateMeRequest) -> User:
    if req.username is not None:
        existing = await db.execute(
            select(User).where(User.username == req.username, User.id != user.id)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Username already taken")
        user.username = req.username
    await db.flush()
    await db.refresh(user, ["role"])
    return user


async def list_users(
    db: AsyncSession, page: int = 1, page_size: int = 20
) -> tuple[list[User], int]:
    offset = (page - 1) * page_size
    result = await db.execute(
        select(User).options(selectinload(User.role)).offset(offset).limit(page_size)
    )
    users = list(result.scalars().all())
    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar_one()
    return users, total


async def admin_update_user(
    db: AsyncSession, user_id: int, req: AdminUpdateUserRequest
) -> User:
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    if req.role is not None:
        role_result = await db.execute(select(Role).where(Role.name == req.role))
        role = role_result.scalar_one_or_none()
        if not role:
            raise ValueError(f"Role '{req.role}' not found")
        user.role_id = role.id

    if req.is_active is not None:
        user.is_active = req.is_active

    await db.flush()
    await db.refresh(user, ["role"])
    return user
