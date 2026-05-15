"""Модель приёмки товаров."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ReceiptItem:
    """Элемент приёмки (товар в приёмке)."""

    product_id: str
    product_name: str
    barcode: str
    quantity: int
    price: float
    cell_code: str = ""

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "barcode": self.barcode,
            "quantity": self.quantity,
            "price": self.price,
            "cell_code": self.cell_code,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReceiptItem":
        return cls(
            product_id=data.get("product_id", ""),
            product_name=data.get("product_name", ""),
            barcode=data.get("barcode", ""),
            quantity=data.get("quantity", 0),
            price=data.get("price", 0.0),
            cell_code=data.get("cell_code", ""),
        )


@dataclass
class Receipt:
    """Приёмка товаров."""

    _id: Any = None
    number: str = ""
    date: datetime | None = None
    items: list[ReceiptItem] = field(default_factory=list)
    status: str = "draft"  # draft, confirmed, cancelled
    created_by: str = ""
    confirmed_at: datetime | None = None
    warehouse_id: str = ""

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "date": self.date or datetime.utcnow(),
            "items": [item.to_dict() for item in self.items],
            "status": self.status,
            "created_by": self.created_by,
            "confirmed_at": self.confirmed_at,
            "warehouse_id": self.warehouse_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Receipt":
        items = [ReceiptItem.from_dict(i) for i in data.get("items", [])]
        return cls(
            _id=data.get("_id"),
            number=data.get("number", ""),
            date=data.get("date"),
            items=items,
            status=data.get("status", "draft"),
            created_by=data.get("created_by", ""),
            confirmed_at=data.get("confirmed_at"),
            warehouse_id=data.get("warehouse_id", ""),
        )

    @property
    def total(self) -> float:
        """Общая сумма приёмки."""
        return sum(item.price * item.quantity for item in self.items)

    @property
    def total_quantity(self) -> int:
        """Общее количество."""
        return sum(item.quantity for item in self.items)
