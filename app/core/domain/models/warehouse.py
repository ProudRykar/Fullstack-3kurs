"""Модель склада."""

from dataclasses import dataclass
from datetime import datetime

from bson import ObjectId


@dataclass
class Warehouse:
    _id: ObjectId | None = None
    name: str = ""
    location: str = ""
    cell_count: int = 0
    capacity_per_cell: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def id(self) -> str:
        return str(self._id) if self._id else ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "location": self.location,
            "cell_count": self.cell_count,
            "capacity_per_cell": self.capacity_per_cell,
            "created_at": self.created_at or datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Warehouse":
        return cls(
            _id=data.get("_id"),
            name=data.get("name", ""),
            location=data.get("location", ""),
            cell_count=data.get("cell_count", 0),
            capacity_per_cell=data.get("capacity_per_cell", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
