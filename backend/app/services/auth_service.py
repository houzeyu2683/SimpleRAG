from __future__ import annotations
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.role import Role, RoleName
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse

log = structlog.get_logger()


async def _get_role(db: AsyncSession, name: str) -> Role:
    result = await db.execute(select(Role).where(Role.name == name))
    role = result.scalar_one_or_none()
    if role is None:
        raise ValueError(f"Role '{name}' not found")
    return role


async def register(db: AsyncSession, req: RegisterRequest) -> User:
    existing = await db.execute(
        select(User).where((User.email == req.email) | (User.username == req.username))
    )
    if existing.scalar_one_or_none():
        raise ValueError("Email or username already taken")

    role = await _get_role(db, RoleName.user.value)
    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
        role_id=role.id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user, ["role"])
    log.info("user.registered", user_id=user.id, email=user.email)
    return user


async def login(db: AsyncSession, email: str, password: str) -> TokenResponse:
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")
    if not user.is_active:
        raise ValueError("Account is disabled")

    access_token = create_access_token(user.id, user.role.name)
    refresh_token = create_refresh_token(user.id)

    user.refresh_token = refresh_token
    await db.flush()

    log.info("user.login", user_id=user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh(db: AsyncSession, token: str) -> TokenResponse:
    try:
        user_id = decode_refresh_token(token)
    except ValueError as exc:
        raise ValueError("Invalid refresh token") from exc

    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user or user.refresh_token != token:
        raise ValueError("Refresh token revoked or invalid")
    if not user.is_active:
        raise ValueError("Account is disabled")

    access_token = create_access_token(user.id, user.role.name)
    new_refresh = create_refresh_token(user.id)
    user.refresh_token = new_refresh
    await db.flush()

    return TokenResponse(access_token=access_token, refresh_token=new_refresh)


async def logout(db: AsyncSession, user_id: int) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.refresh_token = None
        await db.flush()
    log.info("user.logout", user_id=user_id)
