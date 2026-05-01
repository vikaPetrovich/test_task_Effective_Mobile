from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.blacklisted_tokens import BlacklistedToken


async def add_token_to_blacklist(
    db: AsyncSession,
    jti: str,
    user_id: int,
    expires_at: datetime,
):
    result = await db.execute(
        select(BlacklistedToken).where(BlacklistedToken.jti == jti)
    )
    existing_token = result.scalars().first()

    if existing_token:
        return existing_token

    blacklisted_token = BlacklistedToken(
        jti=jti,
        user_id=user_id,
        expires_at=expires_at,
    )

    db.add(blacklisted_token)
    await db.commit()
    await db.refresh(blacklisted_token)

    return blacklisted_token


async def is_token_blacklisted(
    db: AsyncSession,
    jti: str,
) -> bool:
    result = await db.execute(
        select(BlacklistedToken).where(BlacklistedToken.jti == jti)
    )
    blacklisted_token = result.scalars().first()

    return blacklisted_token is not None


def get_token_jti(decoded_token: dict) -> str:
    jti = decoded_token.get("jti")

    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return jti


def get_token_expire_datetime(decoded_token: dict) -> datetime:
    exp = decoded_token.get("exp")

    if not exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return datetime.utcfromtimestamp(exp)