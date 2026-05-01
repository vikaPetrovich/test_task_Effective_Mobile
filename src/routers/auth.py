from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import decode_access_token
from src.db.session import get_db
from src.models.users import User
from src.routers.dependencies import get_current_user, security
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthTokenResponse,
    UserResponse,
)
from src.services.auth_service import register_user, login_user
from src.services.token_blacklist_service import (
    add_token_to_blacklist,
    get_token_expire_datetime,
    get_token_jti,
)


router = APIRouter(prefix="/auth", tags=["Модуль авторизации"])


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Регистрация",
)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    return await register_user(data, db)


@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="Авторизация",
)
async def login(
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await login_user(data, db)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Выход из системы",
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    decoded_token = decode_access_token(token)

    jti = get_token_jti(decoded_token)
    expires_at = get_token_expire_datetime(decoded_token)

    await add_token_to_blacklist(
        db=db,
        jti=jti,
        user_id=current_user.id,
        expires_at=expires_at,
    )

    return {"message": "Successfully logged out"}