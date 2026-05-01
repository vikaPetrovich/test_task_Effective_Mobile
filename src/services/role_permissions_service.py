from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.role_permissions import RolePermission
from src.models.roles import Role
from src.models.system_modules import SystemModule
from src.schemas.role_permissions import (
    RolePermissionUpdateRequest,
    RolePermissionUpdateByNamesRequest,
)


def build_role_permission_response(
    permission: RolePermission,
    role: Role,
    module: SystemModule,
) -> dict:
    return {
        "id": permission.id,
        "role_id": role.id,
        "role_name": role.name,
        "module_id": module.id,
        "module_code": module.code_name,
        "read_own_permission": permission.read_own_permission,
        "read_all_permission": permission.read_all_permission,
        "create_permission": permission.create_permission,
        "update_own_permission": permission.update_own_permission,
        "update_all_permission": permission.update_all_permission,
        "delete_own_permission": permission.delete_own_permission,
        "delete_all_permission": permission.delete_all_permission,
    }


async def get_all_role_permissions(db: AsyncSession):
    result = await db.execute(
        select(RolePermission, Role, SystemModule)
        .join(Role, Role.id == RolePermission.role_id)
        .join(SystemModule, SystemModule.id == RolePermission.module_id)
        .order_by(Role.id, SystemModule.id)
    )

    rows = result.all()

    return [
        build_role_permission_response(
            permission=permission,
            role=role,
            module=module,
        )
        for permission, role, module in rows
    ]


async def get_role_permission_by_id(
    db: AsyncSession,
    permission_id: int,
):
    result = await db.execute(
        select(RolePermission, Role, SystemModule)
        .join(Role, Role.id == RolePermission.role_id)
        .join(SystemModule, SystemModule.id == RolePermission.module_id)
        .where(RolePermission.id == permission_id)
    )

    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role permission not found",
        )

    permission, role, module = row

    return build_role_permission_response(
        permission=permission,
        role=role,
        module=module,
    )


async def update_role_permission(
    db: AsyncSession,
    permission_id: int,
    data: RolePermissionUpdateRequest,
):
    result = await db.execute(
        select(RolePermission).where(RolePermission.id == permission_id)
    )
    permission = result.scalars().first()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role permission not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    for field, value in update_data.items():
        setattr(permission, field, value)

    await db.commit()
    await db.refresh(permission)

    return await get_role_permission_by_id(db, permission.id)

async def update_role_permission_by_names(
    db: AsyncSession,
    data: RolePermissionUpdateByNamesRequest,
):
    result = await db.execute(
        select(RolePermission, Role, SystemModule)
        .join(Role, Role.id == RolePermission.role_id)
        .join(SystemModule, SystemModule.id == RolePermission.module_id)
        .where(Role.name == data.role_name)
        .where(SystemModule.code_name == data.module_code)
    )

    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role permission not found",
        )

    permission, role, module = row

    update_data = data.model_dump(
        exclude_unset=True,
        exclude={"role_name", "module_code"},
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    for field, value in update_data.items():
        setattr(permission, field, value)

    await db.commit()
    await db.refresh(permission)

    return build_role_permission_response(
        permission=permission,
        role=role,
        module=module,
    )