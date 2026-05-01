from fastapi import HTTPException, status
from src.mock.products_data import mock_products


async def get_all_products():
    return mock_products


async def get_product_by_id(product_id: int):
    for product in mock_products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found",
    )


async def create_product(name: str, owner_id: int):
    new_product = {
        "id": len(mock_products) + 1,
        "name": name,
        "owner_id": owner_id,
    }
    mock_products.append(new_product)
    return new_product


async def update_product(product_id: int, name: str):
    for product in mock_products:
        if product["id"] == product_id:
            product["name"] = name
            return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found",
    )


async def delete_product(product_id: int):
    for product in mock_products:
        if product["id"] == product_id:
            mock_products.remove(product)
            return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found",
    )