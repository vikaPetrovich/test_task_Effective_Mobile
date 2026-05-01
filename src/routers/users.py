from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.users import User
from src.routers.dependencies import get_current_user
from src.schemas.users import UserResponse, UserUpdateRequest
from src.services.permissions_service import check_permission
from src.services.users_service import (
    build_user_response,
    get_all_users,
    update_user_profile,
    deactivate_user,
    get_user_by_id,
    get_user_role,
)


router = APIRouter(prefix="/users", tags=["Модуль пользователей"])


@router.get("/me", response_model=UserResponse, summary="Мой профиль")
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="users",
        action="read",
        target_user_id=current_user.id,
    )

    role = await get_user_role(db, current_user.id)

    return build_user_response(user=current_user, role=role)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Обновить мой профиль",
)
async def update_me(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="users",
        action="update",
        target_user_id=current_user.id,
    )

    updated_user = await update_user_profile(
        db=db,
        user=current_user,
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
    )

    role = await get_user_role(db, current_user.id)

    return build_user_response(user=updated_user, role=role)


@router.delete(
    "/me",
    response_model=UserResponse,
    summary="Удалить мой аккаунт",
)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="users",
        action="delete",
        target_user_id=current_user.id,
    )

    deactivated_user = await deactivate_user(db=db, user=current_user)
    role = await get_user_role(db, deactivated_user.id)

    return build_user_response(user=deactivated_user, role=role)


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Список пользователей",
)
async def list_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="users",
        action="read",
    )

    return await get_all_users(db)


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    summary="Деактивировать пользователя",
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="users",
        action="delete",
        target_user_id=user_id,
    )

    target_user = await get_user_by_id(db, user_id)
    deactivated_user = await deactivate_user(db=db, user=target_user)
    role = await get_user_role(db, deactivated_user.id)

    return build_user_response(user=deactivated_user, role=role)