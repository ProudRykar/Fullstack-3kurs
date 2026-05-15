"""Эндпоинты для складов."""

from litestar import Router, delete, get, patch, post
from litestar.dto import DataclassDTO
from litestar.openapi import ResponseSpec
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from punq import Container

from app.api.schemas.user_dto import UserDTO
from app.api.schemas.warehouse_dto import (
    CellCreateDTO,
    CellDTO,
    CellPlaceProductDTO,
    WarehouseCreateDTO,
    WarehouseDTO,
    WarehouseUpdateDTO,
)
from app.core.domain.models.permission import Permission
from app.core.middleware.rbac import require_permission
from app.core.services.product_service import ProductService
from app.core.services.warehouse_service import WarehouseService


@post(
    "/",
    summary="Создать склад",
    tags=["Склады"],
    status_code=HTTP_201_CREATED,
    dependencies={"current_user": require_permission(Permission.WAREHOUSE_CREATE)},
    dto=DataclassDTO[WarehouseCreateDTO],
    return_dto=DataclassDTO[WarehouseDTO],
)
async def create_warehouse(
    data: WarehouseCreateDTO,
    container: Container,
    current_user: UserDTO,
) -> WarehouseDTO:
    service = container.resolve(WarehouseService)
    warehouse = await service.create(
        name=data.name,
        location=data.location,
        cell_count=data.cell_count,
        capacity_per_cell=data.capacity_per_cell,
    )
    return WarehouseDTO.from_warehouse(warehouse)


@get(
    "/",
    summary="Список складов",
    tags=["Склады"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.WAREHOUSE_VIEW)},
)
async def list_warehouses(
    container: Container,
    current_user: UserDTO,
) -> list[WarehouseDTO]:
    service = container.resolve(WarehouseService)
    warehouses = await service.get_all()
    return [WarehouseDTO.from_warehouse(w) for w in warehouses]


@get(
    "/{warehouse_id:str}",
    summary="Получить склад",
    tags=["Склады"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.WAREHOUSE_VIEW)},
    return_dto=DataclassDTO[WarehouseDTO],
)
async def get_warehouse(
    warehouse_id: str,
    container: Container,
    current_user: UserDTO,
) -> WarehouseDTO:
    service = container.resolve(WarehouseService)
    warehouse = await service.get_by_id(warehouse_id)
    if not warehouse:
        raise ValueError("Склад не найден")
    return WarehouseDTO.from_warehouse(warehouse)


@patch(
    "/{warehouse_id:str}",
    summary="Обновить склад",
    tags=["Склады"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.WAREHOUSE_UPDATE)},
    dto=DataclassDTO[WarehouseUpdateDTO],
    return_dto=DataclassDTO[WarehouseDTO],
)
async def update_warehouse(
    warehouse_id: str,
    data: WarehouseUpdateDTO,
    container: Container,
    current_user: UserDTO,
) -> WarehouseDTO:
    service = container.resolve(WarehouseService)
    warehouse = await service.update(
        warehouse_id,
        name=data.name,
        location=data.location,
        cell_count=data.cell_count,
        capacity_per_cell=data.capacity_per_cell,
    )
    if not warehouse:
        raise ValueError("Склад не найден")
    return WarehouseDTO.from_warehouse(warehouse)


@delete(
    "/{warehouse_id:str}",
    summary="Удалить склад",
    tags=["Склады"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.WAREHOUSE_DELETE)},
)
async def delete_warehouse(
    warehouse_id: str,
    container: Container,
    current_user: UserDTO,
) -> dict:
    service = container.resolve(WarehouseService)
    success = await service.delete(warehouse_id)
    if not success:
        raise ValueError("Склад не найден")
    return {"detail": "Склад удалён"}


@post(
    "/{warehouse_id:str}/cells",
    summary="Создать ячейку",
    tags=["Склады"],
    status_code=HTTP_201_CREATED,
    dependencies={"current_user": require_permission(Permission.WAREHOUSE_CELL_CREATE)},
    dto=DataclassDTO[CellCreateDTO],
    return_dto=DataclassDTO[CellDTO],
)
async def create_cell(
    warehouse_id: str,
    data: CellCreateDTO,
    container: Container,
    current_user: UserDTO,
) -> CellDTO:
    service = container.resolve(WarehouseService)
    wh = await service.get_by_id(warehouse_id)
    capacity = wh.capacity_per_cell if wh else 0
    cell = await service.create_cell(warehouse_id, code=data.code, capacity=capacity)
    return CellDTO.from_cell(cell)


@get(
    "/{warehouse_id:str}/cells",
    summary="Ячейки склада",
    tags=["Склады"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.WAREHOUSE_VIEW)},
)
async def list_cells(
    warehouse_id: str,
    container: Container,
    current_user: UserDTO,
) -> list[CellDTO]:
    service = container.resolve(WarehouseService)
    cells = await service.get_cells(warehouse_id)
    return [CellDTO.from_cell(c) for c in cells]


@patch(
    "/{warehouse_id:str}/cells/{cell_id:str}/place",
    summary="Разместить товар в ячейке",
    tags=["Склады"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.WAREHOUSE_CELL_PLACE)},
    dto=DataclassDTO[CellPlaceProductDTO],
    return_dto=DataclassDTO[CellDTO],
)
async def place_product(
    warehouse_id: str,
    cell_id: str,
    data: CellPlaceProductDTO,
    container: Container,
    current_user: UserDTO,
) -> CellDTO:
    service = container.resolve(WarehouseService)
    product_service = container.resolve(ProductService)

    product = await product_service.find_by_code(data.product_barcode)
    if not product:
        raise ValueError("Товар не найден")

    cell = await service.place_product_in_cell(
        cell_id=cell_id,
        product_id=product.id,
        product_name=product.name,
        product_barcode=product.barcode,
        quantity=data.quantity,
    )
    if not cell:
        raise ValueError("Ячейка занята или не найдена")

    return CellDTO.from_cell(cell)


@post(
    "/{warehouse_id:str}/cells/{cell_id:str}/remove",
    summary="Изъять товар из ячейки",
    tags=["Склады"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.WAREHOUSE_CELL_PLACE)},
    return_dto=DataclassDTO[CellDTO],
)
async def remove_product(
    warehouse_id: str,
    cell_id: str,
    container: Container,
    current_user: UserDTO,
) -> CellDTO:
    service = container.resolve(WarehouseService)
    cell = await service.remove_product_from_cell(cell_id)
    if not cell:
        raise ValueError("Ячейка не найдена")
    return CellDTO.from_cell(cell)


@delete(
    "/{warehouse_id:str}/cells/{cell_id:str}",
    summary="Удалить ячейку",
    tags=["Склады"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": require_permission(Permission.WAREHOUSE_CELL_DELETE)},
)
async def delete_cell(
    warehouse_id: str,
    cell_id: str,
    container: Container,
    current_user: UserDTO,
) -> dict:
    service = container.resolve(WarehouseService)
    success = await service.delete_cell(cell_id)
    if not success:
        raise ValueError("Ячейка не найдена")
    return {"detail": "Ячейка удалена"}


warehouses_router = Router(
    path="/warehouses",
    tags=["Склады"],
    route_handlers=[
        create_warehouse,
        list_warehouses,
        get_warehouse,
        update_warehouse,
        delete_warehouse,
        create_cell,
        list_cells,
        place_product,
        remove_product,
        delete_cell,
    ],
)
