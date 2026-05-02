from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.users import User
from src.routers.dependencies import get_current_user
from src.services.permissions_service import check_permission
from src.services.user_role_management_service import (
    assign_role_to_user,
)
from src.schemas.user_roles import (
    AssignRoleRequest,
    AssignRoleResponse,
)
from src.services.access_rules_service import (
    get_all_role_permissions,
    update_role_permission_by_names,
)
from src.schemas.role_permissions import (
    RolePermissionResponse,
    RolePermissionUpdateByNamesRequest,
)

router = APIRouter(
    prefix="/user-role-management",
    tags=["Управление ролями и правами доступа"],
)


@router.patch(
    "/users/{user_id}/role",
    response_model=AssignRoleResponse,
    summary="Назначить роль пользователю",
)
async def assign_user_role(
    user_id: int,
    data: AssignRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="user_role_management",
        action="update",
    )

    return await assign_role_to_user(
        db=db,
        user_id=user_id,
        role_name=data.role_name,
    )


@router.get(
    "/permissions",
    response_model=list[RolePermissionResponse],
    summary="Получить список правил доступа",
)
async def list_role_permissions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="user_role_management",
        action="read",
    )

    return await get_all_role_permissions(db)


@router.patch(
    "/permissions",
    response_model=RolePermissionResponse,
    summary="Изменить правило доступа по роли и модулю",
)
async def patch_role_permission_by_names(
    data: RolePermissionUpdateByNamesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="user_role_management",
        action="update",
    )

    return await update_role_permission_by_names(
        db=db,
        data=data,
    )

