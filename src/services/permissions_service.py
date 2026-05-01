from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.system_modules import SystemModule
from src.models.role_permissions import RolePermission
from src.services.users_service import get_user_role


async def check_permission(
    db: AsyncSession,
    user_id: int,
    module_code: str,
    action: str,
    target_user_id: int | None = None,
):
    """
    action:
    read
    create
    update
    delete
    """

    # 1. получаем роль пользователя
    role = await get_user_role(db, user_id)
    role_id = role.id

    if not role_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role not assigned",
        )

    # 2. получаем модуль
    result = await db.execute(
        select(SystemModule).where(SystemModule.code_name == module_code)
    )
    module = result.scalars().first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System module not found",
        )

    # 3. получаем permission запись
    result = await db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.module_id == module.id,
        )
    )
    permission = result.scalars().first()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    is_own_object = target_user_id is not None and user_id == target_user_id

    # 4. read
    if action == "read":
        if permission.read_all_permission:
            return True
        if permission.read_own_permission and is_own_object:
            return True

    # 5. create
    if action == "create":
        if permission.create_permission:
            return True

    # 6. update
    if action == "update":
        if permission.update_all_permission:
            return True
        if permission.update_own_permission and is_own_object:
            return True

    # 7. delete
    if action == "delete":
        if permission.delete_all_permission:
            return True
        if permission.delete_own_permission and is_own_object:
            return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions",
    )