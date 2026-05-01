from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.models.roles import Role
from src.models.user_roles import UserRole


async def assign_role_to_user(
    db: AsyncSession,
    user_id: int,
    role_name: str,
):
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    role_result = await db.execute(
        select(Role).where(Role.name == role_name)
    )
    role = role_result.scalars().first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    user_role_result = await db.execute(
        select(UserRole).where(UserRole.user_id == user.id)
    )
    user_role = user_role_result.scalars().first()

    if user_role:
        user_role.role_id = role.id
    else:
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
        )
        db.add(user_role)

    await db.commit()
    await db.refresh(user_role)

    return {
        "user_id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        "role_id": role.id,
        "role_name": role.name,
    }