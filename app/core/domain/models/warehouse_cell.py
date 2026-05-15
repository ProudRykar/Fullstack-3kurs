"""Модель ячейки склада."""

from dataclasses import dataclass
from datetime import datetime

from bson import ObjectId


@dataclass
class WarehouseCell:
    _id: ObjectId | None = None
    warehouse_id: str = ""
    code: str = ""
    capacity: int = 0
    product_id: str | None = None
    product_name: str | None = None
    product_barcode: str | None = None
    quantity: int = 0
    updated_at: datetime | None = None

    @property
    def id(self) -> str:
        return str(self._id) if self._id else ""

    @property
    def is_empty(self) -> bool:
        return self.product_id is None

    @property
    def is_full(self) -> bool:
        return not self.is_empty and self.quantity >= self.capacity

    @property
    def available_space(self) -> int:
        if self.is_empty:
            return self.capacity
        return max(0, self.capacity - self.quantity)

    def to_dict(self) -> dict:
        return {
            "warehouse_id": self.warehouse_id,
            "code": self.code,
            "capacity": self.capacity,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_barcode": self.product_barcode,
            "quantity": self.quantity,
            "updated_at": datetime.utcnow(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WarehouseCell":
        return cls(
            _id=data.get("_id"),
            warehouse_id=data.get("warehouse_id", ""),
            code=data.get("code", ""),
            capacity=data.get("capacity", 0),
            product_id=data.get("product_id"),
            product_name=data.get("product_name"),
            product_barcode=data.get("product_barcode"),
            quantity=data.get("quantity", 0),
            updated_at=data.get("updated_at"),
        )
