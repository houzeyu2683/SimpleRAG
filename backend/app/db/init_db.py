from __future__ import annotations
import asyncio
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.role import Role, RoleName
from app.models.user import User

log = structlog.get_logger()
settings = get_settings()


async def seed_admin(db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.email == settings.seed_admin_email))
    if result.scalar_one_or_none():
        log.info("seed.admin.exists", email=settings.seed_admin_email)
        return

    role_result = await db.execute(select(Role).where(Role.name == RoleName.admin.value))
    admin_role = role_result.scalar_one_or_none()
    if not admin_role:
        raise RuntimeError("Admin role not found — run migrations first")

    admin = User(
        username=settings.seed_admin_username,
        email=settings.seed_admin_email,
        hashed_password=hash_password(settings.seed_admin_password),
        role_id=admin_role.id,
    )
    db.add(admin)
    await db.commit()
    log.info("seed.admin.created", email=settings.seed_admin_email)


async def main() -> None:
    async with AsyncSessionLocal() as db:
        await seed_admin(db)


if __name__ == "__main__":
    asyncio.run(main())
