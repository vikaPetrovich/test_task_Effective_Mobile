import asyncio

from sqlalchemy import select

from src.db.session import AsyncSessionLocal
from src.models.roles import Role
from src.models.system_modules import SystemModule
from src.models.role_permissions import RolePermission
from src.models.users import User
from src.models.user_roles import UserRole
from src.core.security import hash_password


async def get_or_create_role(db, name: str, description: str):
    result = await db.execute(select(Role).where(Role.name == name))
    role = result.scalars().first()

    if role:
        return role

    role = Role(name=name, description=description)
    db.add(role)
    await db.flush()
    return role


async def get_or_create_module(db, code_name: str, description: str):
    result = await db.execute(
        select(SystemModule).where(SystemModule.code_name == code_name)
    )
    module = result.scalars().first()

    if module:
        return module

    module = SystemModule(code_name=code_name, description=description)
    db.add(module)
    await db.flush()
    return module


async def create_permission(
    db,
    role_id: int,
    module_id: int,
    read_own=False,
    read_all=False,
    create=False,
    update_own=False,
    update_all=False,
    delete_own=False,
    delete_all=False,
):
    result = await db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.module_id == module_id,
        )
    )
    existing = result.scalars().first()

    if existing:
        return existing

    permission = RolePermission(
        role_id=role_id,
        module_id=module_id,
        read_own_permission=read_own,
        read_all_permission=read_all,
        create_permission=create,
        update_own_permission=update_own,
        update_all_permission=update_all,
        delete_own_permission=delete_own,
        delete_all_permission=delete_all,
    )

    db.add(permission)
    await db.flush()
    return permission


async def create_admin_user(db, admin_role_id: int):
    result = await db.execute(
        select(User).where(User.email == "admin@example.com")
    )
    admin = result.scalars().first()

    if not admin:
        admin = User(
            email="admin@example.com",
            first_name="Администратор",
            last_name="Системы",
            middle_name=None,
            hashed_password=hash_password("admin123"),
            is_active=True,
        )
        db.add(admin)
        await db.flush()

    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == admin.id,
            UserRole.role_id == admin_role_id,
        )
    )
    existing_role = result.scalars().first()

    if not existing_role:
        db.add(UserRole(user_id=admin.id, role_id=admin_role_id))


async def seed():
    async with AsyncSessionLocal() as db:
        admin = await get_or_create_role(db, "admin", "Администратор системы")
        seller = await get_or_create_role(db, "seller", "Продавец")
        buyer = await get_or_create_role(db, "buyer", "Покупатель")

        products = await get_or_create_module(
            db,
            "products",
            "Модуль управления товарами")
        users = await get_or_create_module(
            db,
            "users",
            "Модуль управления пользователями")
        user_role_management = await get_or_create_module(
            db,
            "user_role_management",
            "Модуль управления ролями и правами доступа",
        )

        # admin permissions
        await create_permission(
            db, admin.id, products.id,
            read_own=True, read_all=True,
            create=True,
            update_own=True, update_all=True,
            delete_own=True, delete_all=True,
        )

        await create_permission(
            db, admin.id, users.id,
            read_own=True, read_all=True,
            create=False,
            update_own=True, update_all=True,
            delete_own=True, delete_all=True,
        )

        await create_permission(
            db, admin.id, user_role_management.id,
            read_own=True, read_all=True,
            create=False,
            update_own=True, update_all=True,
            delete_own=False, delete_all=False,
        )

        # seller permissions
        await create_permission(
            db, seller.id, products.id,
            read_own=True, read_all=True,
            create=True,
            update_own=True, update_all=False,
            delete_own=True, delete_all=False,
        )

        await create_permission(
            db, seller.id, users.id,
            read_own=True, read_all=False,
            create=False,
            update_own=True, update_all=False,
            delete_own=True, delete_all=False,
        )

        await create_permission(
            db, seller.id, user_role_management.id,
        )

        # buyer permissions
        await create_permission(
            db, buyer.id, products.id,
            read_own=True, read_all=True,
            create=False,
            update_own=False, update_all=False,
            delete_own=False, delete_all=False,
        )

        await create_permission(
            db, buyer.id, users.id,
            read_own=True, read_all=False,
            create=False,
            update_own=True, update_all=False,
            delete_own=True, delete_all=False,
        )

        await create_permission(
            db, buyer.id, user_role_management.id,
        )

        await create_admin_user(db, admin.id)

        await db.commit()
        print("Seed completed successfully")


if __name__ == "__main__":
    asyncio.run(seed())