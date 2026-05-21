"""Эндпоинты для товаров."""

from typing import Annotated

from litestar import Router, delete, get, patch, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.dto import DataclassDTO
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_429_TOO_MANY_REQUESTS,
)
from litestar.datastructures import UploadFile
from punq import Container

from app.api.exceptions.problem_factory import ErrorCode, ErrorMeta, problem_factory
from app.api.schemas.product_dto import (
    ProductCreateDTO,
    ProductDTO,
    ProductListDTO,
    ProductSearchDTO,
    ProductSearchResultDTO,
    ProductImageDTO,
)
from app.api.schemas.user_dto import UserDTO
from app.core.domain.models.permission import Permission
from app.core.middleware.rbac import require_permission
from app.core.services.product_service import ProductService
from app.core.services.warehouse_service import WarehouseService


@get(
    "/search",
    summary="Поиск товара",
    description="Поиск товара по штрихкоду, QR-коду или RFID",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.PRODUCT_VIEW)},
    dto=DataclassDTO[ProductSearchDTO],
    return_dto=DataclassDTO[ProductDTO],
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Товар найден",
            data_container=ProductDTO,
        ),
        HTTP_404_NOT_FOUND: ResponseSpec(
            description="Товар не найден",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.NOT_FOUND,
                        detail="Товар не найден",
                    ),
                )
            ],
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Не авторизован",
            data_container=ErrorMeta,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Недостаточно прав",
            data_container=ErrorMeta,
        ),
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много запросов",
            data_container=ErrorMeta,
        ),
    },
)
async def search_product(
    code: str,
    container: Container,
    current_user: UserDTO,
    warehouse_id: str | None = None,
) -> dict:
    """Поиск товара по коду."""
    product_service = container.resolve(ProductService)
    warehouse_service = container.resolve(WarehouseService)

    product = await product_service.find_by_code(code)
    if not product:
        raise ValueError("Товар не найден")

    images = await product_service.get_images(product.id) if product.images else []
    urls = {img["id"]: img["url"] for img in images}
    result = ProductDTO.from_product(product, presigned_urls=urls).__dict__

    if warehouse_id:
        cell = await warehouse_service.find_product_in_warehouse(
            warehouse_id, product.barcode
        )
        if not cell:
            raise ValueError("Товар не найден на этом складе")
        result["cell_code"] = cell.code
        result["cell_quantity"] = cell.quantity
        result["cell_capacity"] = cell.capacity

    return result


@get(
    "/search-by-name",
    summary="Поиск товаров по названию",
    description="Поиск товаров по названию, артикулу или штрихкоду с информацией о ячейках",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.PRODUCT_VIEW)},
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Список найденных товаров",
            data_container=ProductSearchResultDTO,
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Не авторизован",
            data_container=ErrorMeta,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Недостаточно прав",
            data_container=ErrorMeta,
        ),
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много запросов",
            data_container=ErrorMeta,
        ),
    },
)
async def search_products_by_name(
    q: str,
    container: Container,
    current_user: UserDTO,
) -> list[dict]:
    """Поиск товаров по названию/артикулу/штрихкоду."""
    product_service = container.resolve(ProductService)
    warehouse_service = container.resolve(WarehouseService)

    products = await product_service.search(q)

    result = []
    for product in products:
        images = await product_service.get_images(product.id) if product.images else []
        urls = {img["id"]: img["url"] for img in images}
        product_dto = ProductDTO.from_product(product, presigned_urls=urls)
        cells = await warehouse_service.find_cells_by_barcode(product.barcode)
        result.append(
            {
                "product": product_dto.__dict__,
                "cells": cells,
            }
        )

    return result


@get(
    "/{product_id:str}",
    summary="Получить товар",
    description="Получить товар по ID",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.PRODUCT_VIEW)},
    return_dto=DataclassDTO[ProductDTO],
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Товар",
            data_container=ProductDTO,
        ),
        HTTP_404_NOT_FOUND: ResponseSpec(
            description="Товар не найден",
            data_container=ErrorMeta,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Недостаточно прав",
            data_container=ErrorMeta,
        ),
    },
)
async def get_product(
    product_id: str,
    container: Container,
    current_user: UserDTO,
) -> ProductDTO:
    """Получить товар по ID."""
    product_service = container.resolve(ProductService)

    product = await product_service.get_by_id(product_id)
    if not product:
        raise ValueError("Товар не найден")

    return ProductDTO.from_product(product)


@post(
    "/",
    summary="Создать товар",
    description="Создать новый товар",
    tags=["Товары"],
    status_code=HTTP_201_CREATED,
    dependencies={"current_user": require_permission(Permission.PRODUCT_CREATE)},
    dto=DataclassDTO[ProductCreateDTO],
    return_dto=DataclassDTO[ProductDTO],
    responses={
        HTTP_201_CREATED: ResponseSpec(
            description="Товар создан",
            data_container=ProductDTO,
        ),
        HTTP_400_BAD_REQUEST: ResponseSpec(
            description="Ошибка",
            data_container=ErrorMeta,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Недостаточно прав",
            data_container=ErrorMeta,
        ),
    },
)
async def create_product(
    data: ProductCreateDTO,
    container: Container,
    current_user: UserDTO,
) -> ProductDTO:
    """Создать товар."""
    product_service = container.resolve(ProductService)

    product = await product_service.create(
        name=data.name,
        sku=data.sku,
        barcode=data.barcode,
        category=data.category or "",
        location=data.location or "",
        price=data.price,
        weight=data.weight,
        height=data.height,
        width=data.width,
        length=data.length,
        qrcode=data.qrcode,
        rfid=data.rfid,
    )

    return ProductDTO.from_product(product)


@patch(
    "/{product_id:str}",
    summary="Обновить товар",
    description="Обновить товар",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.PRODUCT_UPDATE)},
    dto=DataclassDTO[ProductCreateDTO],
    return_dto=DataclassDTO[ProductDTO],
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Товар обновлён",
            data_container=ProductDTO,
        ),
        HTTP_404_NOT_FOUND: ResponseSpec(
            description="Товар не найден",
            data_container=ErrorMeta,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Недостаточно прав",
            data_container=ErrorMeta,
        ),
    },
)
async def update_product(
    product_id: str,
    data: ProductCreateDTO,
    container: Container,
    current_user: UserDTO,
) -> ProductDTO:
    """Обновить товар."""
    product_service = container.resolve(ProductService)

    product = await product_service.update(
        product_id,
        name=data.name,
        sku=data.sku,
        barcode=data.barcode,
        category=data.category or "",
        location=data.location or "",
        price=data.price,
        qrcode=data.qrcode,
        rfid=data.rfid,
        quantity=data.quantity,
    )

    if not product:
        raise ValueError("Товар не найден")

    return ProductDTO.from_product(product)


@delete(
    "/{product_id:str}",
    summary="Удалить товар",
    description="Удалить товар",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.PRODUCT_DELETE)},
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Товар удалён",
            data_container=None,
        ),
        HTTP_404_NOT_FOUND: ResponseSpec(
            description="Товар не найден",
            data_container=ErrorMeta,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Недостаточно прав",
            data_container=ErrorMeta,
        ),
    },
)
async def delete_product(
    product_id: str,
    container: Container,
    current_user: UserDTO,
) -> dict:
    """Удалить товар."""
    product_service = container.resolve(ProductService)

    success = await product_service.delete(product_id)
    if not success:
        raise ValueError("Товар не найден")

    return {"detail": "Товар удалён"}


@get(
    "/categories",
    summary="Список категорий",
    description="Получить список всех категорий товаров",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.PRODUCT_VIEW)},
)
async def list_categories(
    container: Container,
    current_user: UserDTO,
) -> list[str]:
    """Получить список всех категорий."""
    product_service = container.resolve(ProductService)
    return await product_service.get_categories()


@get(
    "/",
    summary="Список всех товаров",
    description="Получить список всех товаров с фильтрацией, сортировкой и пагинацией",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.PRODUCT_VIEW)},
    return_dto=DataclassDTO[ProductListDTO],
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Список товаров",
            data_container=ProductListDTO,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Недостаточно прав",
            data_container=ErrorMeta,
        ),
    },
)
async def list_products(
    container: Container,
    current_user: UserDTO,
    limit: int = 100,
    skip: int = 0,
    search: str = "",
    category: str = "",
    min_price: float = 0,
    max_price: float = 0,
    sort_by: str = "name",
    sort_order: str = "asc",
) -> ProductListDTO:
    """Получить список всех товаров с фильтрацией."""
    product_service = container.resolve(ProductService)
    products, total = await product_service.get_all(
        limit=limit,
        skip=skip,
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    dtos = []
    for p in products:
        images = await product_service.get_images(p.id) if p.images else []
        urls = {img["id"]: img["url"] for img in images}
        dtos.append(ProductDTO.from_product(p, presigned_urls=urls))

    return ProductListDTO(
        items=dtos,
        total=total,
    )


@post(
    "/{product_id:str}/images",
    summary="Загрузить изображение товара",
    description="Загрузить изображение для товара",
    tags=["Товары"],
    status_code=HTTP_201_CREATED,
    dependencies={"current_user": require_permission(Permission.PRODUCT_UPDATE)},
    responses={
        HTTP_201_CREATED: ResponseSpec(
            description="Изображение загружено",
            data_container=None,
        ),
        HTTP_400_BAD_REQUEST: ResponseSpec(
            description="Ошибка",
            data_container=ErrorMeta,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Недостаточно прав",
            data_container=ErrorMeta,
        ),
        HTTP_404_NOT_FOUND: ResponseSpec(
            description="Товар не найден",
            data_container=ErrorMeta,
        ),
    },
)
async def upload_product_image(
    product_id: str,
    data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
    container: Container,
    current_user: UserDTO,
) -> dict:
    """Загрузить изображение для товара."""
    product_service = container.resolve(ProductService)
    result = await product_service.upload_image(
        product_id=product_id,
        file=data,
    )
    return result


@get(
    "/{product_id:str}/images",
    summary="Изображения товара",
    description="Получить изображения товара с presigned URLs",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.PRODUCT_VIEW)},
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Список изображений",
            data_container=None,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Недостаточно прав",
            data_container=ErrorMeta,
        ),
        HTTP_404_NOT_FOUND: ResponseSpec(
            description="Товар не найден",
            data_container=ErrorMeta,
        ),
    },
)
async def get_product_images(
    product_id: str,
    container: Container,
    current_user: UserDTO,
) -> list[dict]:
    """Получить изображения товара."""
    product_service = container.resolve(ProductService)
    return await product_service.get_images(product_id)


@delete(
    "/{product_id:str}/images/{image_id:str}",
    summary="Удалить изображение товара",
    description="Удалить изображение товара",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.PRODUCT_UPDATE)},
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Изображение удалено",
            data_container=None,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Недостаточно прав",
            data_container=ErrorMeta,
        ),
        HTTP_404_NOT_FOUND: ResponseSpec(
            description="Изображение не найдено",
            data_container=ErrorMeta,
        ),
    },
)
async def delete_product_image(
    product_id: str,
    image_id: str,
    container: Container,
    current_user: UserDTO,
) -> dict:
    """Удалить изображение товара."""
    product_service = container.resolve(ProductService)
    success = await product_service.delete_image(product_id, image_id)
    if not success:
        raise ValueError("Изображение не найдено")
    return {"detail": "Изображение удалено"}


products_router = Router(
    path="/products",
    tags=["Товары"],
    route_handlers=[
        list_products,
        list_categories,
        search_product,
        search_products_by_name,
        get_product,
        create_product,
        update_product,
        delete_product,
        upload_product_image,
        get_product_images,
        delete_product_image,
    ],
)
