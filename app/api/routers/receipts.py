"""Эндпоинты для приёмок."""

from typing import Any

from bson import ObjectId
from litestar import Router, delete, get, post
from litestar.di import Provide
from litestar.dto import DTOConfig
from litestar.openapi import ResponseSpec
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from punq import Container

from app.api.schemas.receipt_dto import ReceiptCreateItemDTO, ReceiptDTO
from app.core.services.auth_service import AuthService
from app.core.services.product_service import ProductService
from app.core.services.receipt_service import ReceiptService
from app.api.schemas.user_dto import UserDTO


@post(
    "/",
    summary="Создать приёмку",
    tags=["Приёмка"],
    status_code=HTTP_201_CREATED,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def create_receipt(
    container: Container,
    current_user: UserDTO | None,
) -> dict:
    receipt_service = container.resolve(ReceiptService)
    user_id = current_user.id if current_user else ""

    receipt = await receipt_service.create(user_id)
    return {
        "id": str(receipt._id) if receipt._id else "",
        "number": receipt.number,
        "status": receipt.status,
    }


@get(
    "/",
    summary="Список приёмок",
    tags=["Приёмка"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def list_receipts(
    container: Container,
    current_user: UserDTO | None,
) -> list[dict]:
    receipt_service = container.resolve(ReceiptService)
    receipts = await receipt_service.get_all()

    return [
        {
            "id": str(r._id) if r._id else "",
            "number": r.number,
            "date": r.date.isoformat() if r.date else None,
            "status": r.status,
            "total": r.total,
            "total_quantity": r.total_quantity,
        }
        for r in receipts
    ]


@get(
    "/{receipt_id:str}",
    summary="Получить приёмку",
    tags=["Приёмка"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def get_receipt(
    receipt_id: str,
    container: Container,
    current_user: UserDTO | None,
) -> dict:
    receipt_service = container.resolve(ReceiptService)
    receipt = await receipt_service.get_by_id(receipt_id)

    if not receipt:
        raise ValueError("Приёмка не найдена")

    return {
        "id": str(receipt._id) if receipt._id else "",
        "number": receipt.number,
        "date": receipt.date.isoformat() if receipt.date else None,
        "items": [
            {
                "product_id": i.product_id,
                "product_name": i.product_name,
                "barcode": i.barcode,
                "quantity": i.quantity,
                "price": i.price,
            }
            for i in receipt.items
        ],
        "status": receipt.status,
        "total": receipt.total,
        "total_quantity": receipt.total_quantity,
    }


@post(
    "/{receipt_id:str}/items",
    summary="Добавить товар в приёмку",
    tags=["Приёмка"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def add_item(
    receipt_id: str,
    barcode: str,
    quantity: int,
    price: float,
    container: Container,
    current_user: UserDTO | None,
) -> dict:
    receipt_service = container.resolve(ReceiptService)
    product_service = container.resolve(ProductService)

    product = await product_service.find_by_code(barcode)
    if not product:
        raise ValueError("Товар не найден")

    receipt = await receipt_service.add_item(
        receipt_id=receipt_id,
        product_id=product.id,
        quantity=quantity,
        price=price,
    )

    if not receipt:
        raise ValueError("Не удалось добавить товар")

    return {"status": "ok"}


@post(
    "/{receipt_id:str}/confirm",
    summary="Подтвердить приёмку",
    tags=["Приёмка"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def confirm_receipt(
    receipt_id: str,
    container: Container,
    current_user: UserDTO | None,
) -> dict:
    receipt_service = container.resolve(ReceiptService)
    receipt = await receipt_service.confirm(receipt_id)

    if not receipt:
        raise ValueError("Не удалось подтвердить приёмку")

    return {"status": "confirmed"}


@post(
    "/{receipt_id:str}/cancel",
    summary="Отменить приёмку",
    tags=["Приёмка"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def cancel_receipt(
    receipt_id: str,
    container: Container,
    current_user: UserDTO | None,
) -> dict:
    receipt_service = container.resolve(ReceiptService)
    receipt = await receipt_service.cancel(receipt_id)

    if not receipt:
        raise ValueError("Не удалось отменить приёмку")

    return {"status": "cancelled"}


receipts_router = Router(
    path="/receipts",
    tags=["Приёмка"],
    route_handlers=[
        create_receipt,
        list_receipts,
        get_receipt,
        add_item,
        confirm_receipt,
        cancel_receipt,
    ],
)
