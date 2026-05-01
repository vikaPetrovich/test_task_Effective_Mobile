from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.models.roles import Role
from src.models.user_roles import UserRole

from src.core.security import hash_password, verify_password, create_access_token


async def register_user(data, db: AsyncSession):
    if data.password != data.password_repeat:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    result = await db.execute(select(Role).where(Role.name == "buyer"))
    buyer_role = result.scalars().first()

    if not buyer_role:
        raise HTTPException(status_code=500, detail="Default role buyer not found")

    db_user = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
        hashed_password=hash_password(data.password),
        is_active=True,
    )

    db.add(db_user)
    await db.flush()

    db.add(UserRole(user_id=db_user.id, role_id=buyer_role.id))

    await db.commit()
    await db.refresh(db_user)

    return db_user


async def login_user(data, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
    }