"""Модель инвентаризации."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class InventoryScan:
    """Результат сканирования одного товара."""

    product_id: str
    product_name: str
    barcode: str
    db_quantity: int
    scanned_quantity: int

    @property
    def diff(self) -> int:
        return self.scanned_quantity - self.db_quantity

    @property
    def is_ok(self) -> bool:
        return self.db_quantity == self.scanned_quantity

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "barcode": self.barcode,
            "db_quantity": self.db_quantity,
            "scanned_quantity": self.scanned_quantity,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InventoryScan":
        return cls(
            product_id=data.get("product_id", ""),
            product_name=data.get("product_name", ""),
            barcode=data.get("barcode", ""),
            db_quantity=data.get("db_quantity", 0),
            scanned_quantity=data.get("scanned_quantity", 0),
        )


@dataclass
class Inventory:
    """Инвентаризация."""

    _id: Any = None
    number: str = ""
    date: datetime | None = None
    scans: list[InventoryScan] = field(default_factory=list)
    status: str = "in_progress"
    created_by: str = ""

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "date": self.date or datetime.utcnow(),
            "scans": [s.to_dict() for s in self.scans],
            "status": self.status,
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Inventory":
        scans = [InventoryScan.from_dict(s) for s in data.get("scans", [])]
        return cls(
            _id=data.get("_id"),
            number=data.get("number", ""),
            date=data.get("date"),
            scans=scans,
            status=data.get("status", "in_progress"),
            created_by=data.get("created_by", ""),
        )

    @property
    def total_checked(self) -> int:
        return len(self.scans)

    @property
    def total_diff(self) -> int:
        return sum(s.diff for s in self.scans)

    @property
    def diff_count(self) -> int:
        return sum(1 for s in self.scans if not s.is_ok)
