from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.models.roles import Role
from src.models.user_roles import UserRole


def build_user_response(user: User, role: Role) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        "is_active": user.is_active,
        "role": role.name,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "deleted_at": user.deleted_at,
    }


async def get_all_users(db: AsyncSession):
    result = await db.execute(
        select(User, Role)
        .join(UserRole, UserRole.user_id == User.id)
        .join(Role, Role.id == UserRole.role_id)
        .order_by(User.id)
    )

    rows = result.all()

    return [
        build_user_response(user=user, role=role)
        for user, role in rows
    ]


async def update_user_profile(
    db: AsyncSession,
    user: User,
    first_name: str | None = None,
    last_name: str | None = None,
    middle_name: str | None = None,
):
    if first_name is not None:
        user.first_name = first_name

    if last_name is not None:
        user.last_name = last_name

    if middle_name is not None:
        user.middle_name = middle_name

    await db.commit()
    await db.refresh(user)

    return user


async def deactivate_user(db: AsyncSession, user: User):
    user.is_active = False
    user.deleted_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return user


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


async def get_user_role(db: AsyncSession, user_id: int) -> Role:
    result = await db.execute(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
    )
    role = result.scalars().first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role not assigned",
        )

    return role