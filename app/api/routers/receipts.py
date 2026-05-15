"""Эндпоинты для приёмок."""

from typing import Any

from bson import ObjectId
from litestar import Router, delete, get, post
from litestar.di import Provide
from litestar.dto import DTOConfig, DataclassDTO
from litestar.openapi import ResponseSpec
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from punq import Container

from app.api.schemas.receipt_dto import ReceiptCreateItemDTO, ReceiptDTO
from app.api.schemas.user_dto import UserDTO
from app.core.domain.models.permission import Permission
from app.core.middleware.rbac import require_permission
from app.core.services.product_service import ProductService
from app.core.services.receipt_service import ReceiptService
from app.core.services.warehouse_service import WarehouseService


@post(
    "/",
    summary="Создать приёмку",
    tags=["Приёмка"],
    status_code=HTTP_201_CREATED,
    dependencies={"current_user": require_permission(Permission.RECEIPT_CREATE)},
)
async def create_receipt(
    container: Container,
    current_user: UserDTO,
    warehouse_id: str = "",
) -> dict:
    receipt_service = container.resolve(ReceiptService)

    receipt = await receipt_service.create(current_user.id, warehouse_id)
    return {
        "id": str(receipt._id) if receipt._id else "",
        "number": receipt.number,
        "status": receipt.status,
        "warehouse_id": receipt.warehouse_id,
    }


@get(
    "/",
    summary="Список приёмок",
    tags=["Приёмка"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.RECEIPT_VIEW)},
)
async def list_receipts(
    container: Container,
    current_user: UserDTO,
    warehouse_id: str | None = None,
) -> list[dict]:
    receipt_service = container.resolve(ReceiptService)
    receipts = await receipt_service.get_all(warehouse_id=warehouse_id)

    return [
        {
            "id": str(r._id) if r._id else "",
            "number": r.number,
            "date": r.date.isoformat() if r.date else None,
            "status": r.status,
            "total": r.total,
            "total_quantity": r.total_quantity,
            "warehouse_id": r.warehouse_id,
        }
        for r in receipts
    ]


@get(
    "/{receipt_id:str}",
    summary="Получить приёмку",
    tags=["Приёмка"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.RECEIPT_VIEW)},
)
async def get_receipt(
    receipt_id: str,
    container: Container,
    current_user: UserDTO,
) -> dict:
    receipt_service = container.resolve(ReceiptService)
    warehouse_service = container.resolve(WarehouseService)
    receipt = await receipt_service.get_by_id(receipt_id)

    if not receipt:
        raise ValueError("Приёмка не найдена")

    items = []

    if receipt.status == "draft" and receipt.warehouse_id:
        item_list = [{"barcode": i.barcode, "quantity": i.quantity} for i in receipt.items]
        cells_info = await warehouse_service.get_items_cell_info(receipt.warehouse_id, item_list)
    else:
        cells_info = [None] * len(receipt.items)

    for idx, i in enumerate(receipt.items):
        item = {
            "product_id": i.product_id,
            "product_name": i.product_name,
            "barcode": i.barcode,
            "quantity": i.quantity,
            "price": i.price,
        }

        if receipt.status == "confirmed":
            if i.cell_code:
                item["cell_code"] = i.cell_code
                cell = await warehouse_service.get_cell_by_code(receipt.warehouse_id, i.cell_code)
                if cell:
                    item["cell_quantity"] = cell.quantity
                    item["cell_capacity"] = cell.capacity
            elif receipt.warehouse_id:
                cell_info = await warehouse_service.get_product_cell_info(receipt.warehouse_id, i.barcode)
                if cell_info:
                    item["cell_code"] = cell_info["cell_code"]
                    item["cell_quantity"] = cell_info["cell_quantity"]
                    item["cell_capacity"] = cell_info["cell_capacity"]
        elif receipt.status == "draft":
            cell = cells_info[idx]
            if cell:
                item["cell_code"] = cell["cell_code"]
                item["cell_quantity"] = cell["cell_quantity"]
                item["cell_capacity"] = cell["cell_capacity"]

        items.append(item)

    return {
        "id": str(receipt._id) if receipt._id else "",
        "number": receipt.number,
        "date": receipt.date.isoformat() if receipt.date else None,
        "items": items,
        "status": receipt.status,
        "total": receipt.total,
        "total_quantity": receipt.total_quantity,
        "warehouse_id": receipt.warehouse_id,
    }


@post(
    "/{receipt_id:str}/items",
    summary="Добавить товар в приёмку",
    tags=["Приёмка"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.RECEIPT_ADD_ITEM)},
    dto=DataclassDTO[ReceiptCreateItemDTO],
)
async def add_item(
    receipt_id: str,
    data: ReceiptCreateItemDTO,
    container: Container,
    current_user: UserDTO,
) -> dict:
    receipt_service = container.resolve(ReceiptService)
    product_service = container.resolve(ProductService)
    warehouse_service = container.resolve(WarehouseService)

    product = await product_service.find_by_code(data.barcode)
    if not product:
        raise ValueError("Товар не найден")

    receipt = await receipt_service.add_item(
        receipt_id=receipt_id,
        product_id=product.id,
        quantity=data.quantity,
    )

    if not receipt:
        raise ValueError("Не удалось добавить товар")

    result = {"status": "ok"}

    if receipt.warehouse_id:
        pending_qty = sum(i.quantity for i in receipt.items if i.barcode == product.barcode) - data.quantity
        cell_info = await warehouse_service.suggest_cell(receipt.warehouse_id, product.barcode, pending_qty)
        if cell_info:
            result["cell"] = cell_info

    return result


@post(
    "/{receipt_id:str}/confirm",
    summary="Подтвердить приёмку",
    tags=["Приёмка"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.RECEIPT_CONFIRM)},
)
async def confirm_receipt(
    receipt_id: str,
    container: Container,
    current_user: UserDTO,
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
    dependencies={"current_user": require_permission(Permission.RECEIPT_CANCEL)},
)
async def cancel_receipt(
    receipt_id: str,
    container: Container,
    current_user: UserDTO,
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