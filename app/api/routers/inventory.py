"""Эндпоинты для инвентаризации."""

from litestar import Router, get, post
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from punq import Container

from app.api.schemas.user_dto import UserDTO
from app.core.services.auth_service import AuthService
from app.core.services.product_service import ProductService
from app.core.services.inventory_service import InventoryService


@post(
    "/",
    summary="Начать инвентаризацию",
    tags=["Инвентаризация"],
    status_code=HTTP_201_CREATED,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def create_inventory(
    container: Container,
    current_user: UserDTO | None,
) -> dict:
    inv_service = container.resolve(InventoryService)
    user_id = current_user.id if current_user else ""

    inv = await inv_service.create(user_id)
    return {
        "id": str(inv._id) if inv._id else "",
        "number": inv.number,
        "status": inv.status,
    }


@get(
    "/",
    summary="Список инвентаризаций",
    tags=["Инвентаризация"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def list_inventory(
    container: Container,
    current_user: UserDTO | None,
) -> list[dict]:
    inv_service = container.resolve(InventoryService)
    inventory_list = await inv_service.get_all()

    return [
        {
            "id": str(i._id) if i._id else "",
            "number": i.number,
            "date": i.date.isoformat() if i.date else None,
            "status": i.status,
            "total_checked": i.total_checked,
            "diff_count": i.diff_count,
        }
        for i in inventory_list
    ]


@get(
    "/active",
    summary="Активная инвентаризация",
    tags=["Инвентаризация"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def get_active_inventory(
    container: Container,
    current_user: UserDTO | None,
) -> dict | None:
    inv_service = container.resolve(InventoryService)
    inv = await inv_service.get_active()

    if not inv:
        return None

    return {
        "id": str(inv._id) if inv._id else "",
        "number": inv.number,
        "status": inv.status,
        "scans": [
            {
                "product_name": s.product_name,
                "barcode": s.barcode,
                "db_quantity": s.db_quantity,
                "scanned_quantity": s.scanned_quantity,
                "diff": s.diff,
                "is_ok": s.is_ok,
            }
            for s in inv.scans
        ],
    }


@get(
    "/{inventory_id:str}",
    summary="Получить инвентаризацию",
    tags=["Инвентаризация"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def get_inventory(
    inventory_id: str,
    container: Container,
    current_user: UserDTO | None,
) -> dict:
    inv_service = container.resolve(InventoryService)
    inv = await inv_service.get_by_id(inventory_id)

    if not inv:
        raise ValueError("Инвентаризация не найдена")

    return {
        "id": str(inv._id) if inv._id else "",
        "number": inv.number,
        "date": inv.date.isoformat() if inv.date else None,
        "status": inv.status,
        "total_checked": inv.total_checked,
        "diff_count": inv.diff_count,
        "scans": [
            {
                "product_name": s.product_name,
                "barcode": s.barcode,
                "db_quantity": s.db_quantity,
                "scanned_quantity": s.scanned_quantity,
                "diff": s.diff,
                "is_ok": s.is_ok,
            }
            for s in inv.scans
        ],
    }


@post(
    "/{inventory_id:str}/scan",
    summary="Сканировать товар",
    tags=["Инвентаризация"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def scan_inventory(
    inventory_id: str,
    barcode: str,
    scanned_quantity: int,
    container: Container,
    current_user: UserDTO | None,
) -> dict:
    inv_service = container.resolve(InventoryService)
    product_service = container.resolve(ProductService)

    product = await product_service.find_by_code(barcode)
    if not product:
        raise ValueError("Товар не найден")

    inv = await inv_service.scan(inventory_id, barcode, scanned_quantity)
    if not inv:
        raise ValueError("Не удалось добавить скан")

    return {"status": "ok"}


@post(
    "/{inventory_id:str}/complete",
    summary="Завершить инвентаризацию",
    tags=["Инвентаризация"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def complete_inventory(
    inventory_id: str,
    container: Container,
    current_user: UserDTO | None,
) -> dict:
    inv_service = container.resolve(InventoryService)
    inv = await inv_service.complete(inventory_id)

    if not inv:
        raise ValueError("Не удалось завершить")

    return {"status": "completed"}


inventory_router = Router(
    path="/inventory",
    tags=["Инвентаризация"],
    route_handlers=[
        create_inventory,
        list_inventory,
        get_active_inventory,
        get_inventory,
        scan_inventory,
        complete_inventory,
    ],
)
