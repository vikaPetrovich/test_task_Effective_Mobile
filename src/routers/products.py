from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.users import User
from src.routers.dependencies import get_current_user
from src.schemas.products import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
)
from src.services.permissions_service import check_permission
from src.services.product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
)


router = APIRouter(
    prefix="/products",
    tags=["Модуль продуктов"],
)


@router.get(
    "/",
    response_model=list[ProductResponse],
    summary="Список товаров",
)
async def list_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="products",
        action="read",
    )

    return await get_all_products()


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Получить товар по ID",
)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    product = await get_product_by_id(product_id)

    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="products",
        action="read",
        target_user_id=product["owner_id"],
    )

    return product


@router.post(
    "/",
    response_model=ProductResponse,
    summary="Создать товар",
)
async def create_new_product(
    data: ProductCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="products",
        action="create",
    )

    return await create_product(
        name=data.name,
        owner_id=current_user.id,
    )


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Обновить товар",
)
async def update_existing_product(
    product_id: int,
    data: ProductUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    product = await get_product_by_id(product_id)

    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="products",
        action="update",
        target_user_id=product["owner_id"],
    )

    return await update_product(
        product_id=product_id,
        name=data.name,
    )


@router.delete(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Удалить товар",
)
async def delete_existing_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    product = await get_product_by_id(product_id)

    await check_permission(
        db=db,
        user_id=current_user.id,
        module_code="products",
        action="delete",
        target_user_id=product["owner_id"],
    )

    return await delete_product(product_id)