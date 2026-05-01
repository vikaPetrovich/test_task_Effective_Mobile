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
    permission = result.scalars().first()

    if not permission:
        permission = RolePermission(
            role_id=role_id,
            module_id=module_id,
        )
        db.add(permission)

    permission.read_own_permission = read_own
    permission.read_all_permission = read_all
    permission.create_permission = create
    permission.update_own_permission = update_own
    permission.update_all_permission = update_all
    permission.delete_own_permission = delete_own
    permission.delete_all_permission = delete_all

    await db.flush()
    return permission


async def get_or_create_user_with_role(
    db,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    middle_name: str | None,
    role_id: int,
):
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalars().first()

    if not user:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            hashed_password=hash_password(password),
            is_active=True,
        )
        db.add(user)
        await db.flush()

    result = await db.execute(
        select(UserRole).where(UserRole.user_id == user.id)
    )
    user_role = result.scalars().first()

    if user_role:
        user_role.role_id = role_id
    else:
        db.add(UserRole(user_id=user.id, role_id=role_id))

    return user


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

        await get_or_create_user_with_role(
            db=db,
            email="admin@example.com",
            password="admin123",
            first_name="Администратор",
            last_name="Системы",
            middle_name=None,
            role_id=admin.id,
        )

        await get_or_create_user_with_role(
            db=db,
            email="seller@example.com",
            password="seller123",
            first_name="Тестовый",
            last_name="Продавец",
            middle_name=None,
            role_id=seller.id,
        )

        await get_or_create_user_with_role(
            db=db,
            email="buyer@example.com",
            password="buyer123",
            first_name="Тестовый",
            last_name="Покупатель",
            middle_name=None,
            role_id=buyer.id,
        )

        await db.commit()
        print("Seed completed successfully")


if __name__ == "__main__":
    asyncio.run(seed())