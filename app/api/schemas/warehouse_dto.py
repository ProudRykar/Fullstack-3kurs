"""DTO для складов."""

from dataclasses import dataclass

from app.core.domain.models.warehouse import Warehouse
from app.core.domain.models.warehouse_cell import WarehouseCell


@dataclass
class WarehouseCreateDTO:
    name: str
    location: str = ""
    cell_count: int = 0
    capacity_per_cell: int = 0


@dataclass
class WarehouseUpdateDTO:
    name: str
    location: str = ""
    cell_count: int = 0
    capacity_per_cell: int = 0


@dataclass
class WarehouseDTO:
    id: str
    name: str
    location: str
    cell_count: int = 0
    capacity_per_cell: int = 0
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_warehouse(cls, w: Warehouse) -> "WarehouseDTO":
        return cls(
            id=w.id,
            name=w.name,
            location=w.location,
            cell_count=w.cell_count,
            capacity_per_cell=w.capacity_per_cell,
            created_at=w.created_at.isoformat() if w.created_at else None,
            updated_at=w.updated_at.isoformat() if w.updated_at else None,
        )


@dataclass
class CellCreateDTO:
    code: str


@dataclass
class CellPlaceProductDTO:
    product_barcode: str
    quantity: int = 1


@dataclass
class CellDTO:
    id: str
    warehouse_id: str
    code: str
    capacity: int = 0
    product_id: str | None = None
    product_name: str | None = None
    product_barcode: str | None = None
    quantity: int = 0
    is_empty: bool = True

    @classmethod
    def from_cell(cls, c: WarehouseCell) -> "CellDTO":
        return cls(
            id=c.id,
            warehouse_id=c.warehouse_id,
            code=c.code,
            capacity=c.capacity,
            product_id=c.product_id,
            product_name=c.product_name,
            product_barcode=c.product_barcode,
            quantity=c.quantity,
            is_empty=c.is_empty,
        )
