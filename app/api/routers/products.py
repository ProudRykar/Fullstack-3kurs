"""Эндпоинты для товаров."""

from typing import Annotated

from bson import ObjectId
from litestar import Router, delete, get, patch, post
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.dto import DataclassDTO
from litestar.enums import RequestEncodingType
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from litestar.params import Parameter
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_429_TOO_MANY_REQUESTS,
)
from punq import Container

from app.api.exceptions.problem_factory import ErrorCode, ErrorMeta, problem_factory
from app.api.schemas.product_dto import ProductCreateDTO, ProductDTO, ProductSearchDTO
from app.core.domain.models.product import Product
from app.core.services.auth_service import AuthService
from app.core.services.product_service import ProductService


@get(
    "/search",
    summary="Поиск товара",
    description="Поиск товара по штрихкоду, QR-коду или RFID",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
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
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много запросов",
            data_container=ErrorMeta,
        ),
    },
)
async def search_product(
    code: str,
    container: Container,
) -> ProductDTO:
    """Поиск товара по коду."""
    product_service = container.resolve(ProductService)

    product = await product_service.find_by_code(code)
    if not product:
        raise ValueError("Товар не найден")

    return ProductDTO.from_product(product)


@get(
    "/{product_id:str}",
    summary="Получить товар",
    description="Получить товар по ID",
    tags=["Товары"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
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
    },
)
async def get_product(
    product_id: str,
    container: Container,
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
    dependencies={"current_user": Provide(AuthService.get_current_user)},
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
    },
)
async def create_product(
    data: ProductCreateDTO,
    container: Container,
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
    dependencies={"current_user": Provide(AuthService.get_current_user)},
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
    },
)
async def update_product(
    product_id: str,
    data: ProductCreateDTO,
    container: Container,
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
    dependencies={"current_user": Provide(AuthService.get_current_user)},
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Товар удалён",
            data_container=None,
        ),
        HTTP_404_NOT_FOUND: ResponseSpec(
            description="Товар не найден",
            data_container=ErrorMeta,
        ),
    },
)
async def delete_product(
    product_id: str,
    container: Container,
) -> dict:
    """Удалить товар."""
    product_service = container.resolve(ProductService)

    success = await product_service.delete(product_id)
    if not success:
        raise ValueError("Товар не найден")

    return {"detail": "Товар удалён"}


products_router = Router(
    path="/products",
    tags=["Товары"],
    route_handlers=[
        search_product,
        get_product,
        create_product,
        update_product,
        delete_product,
    ],
)
