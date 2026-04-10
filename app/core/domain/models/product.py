"""Модель товара для склада."""

from dataclasses import dataclass
from datetime import datetime
from bson import ObjectId


@dataclass
class Product:
    """Товар на складе.

    Attributes:
        _id: Уникальный ID
        barcode: Штрихкод
        qrcode: QR-код
        rfid: RFID метка
        name: Название товара
        sku: Артикул
        category: Категория
        location: Место хранения
        quantity: Количество на складе
        price: Цена
        created_at: Дата создания
        updated_at: Дата обновления
    """

    _id: ObjectId | None = None
    barcode: str = ""
    qrcode: str | None = None
    rfid: str | None = None
    name: str = ""
    sku: str = ""
    category: str = ""
    location: str = ""
    quantity: int = 0
    price: float = 0.0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def id(self) -> str:
        """Return string ID."""
        return str(self._id) if self._id else ""

    def to_dict(self) -> dict:
        """Convert to dict for DB."""
        return {
            "barcode": self.barcode,
            "qrcode": self.qrcode,
            "rfid": self.rfid,
            "name": self.name,
            "sku": self.sku,
            "category": self.category,
            "location": self.location,
            "quantity": self.quantity,
            "price": self.price,
            "created_at": self.created_at or datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Create from dict."""
        return cls(
            _id=data.get("_id"),
            barcode=data.get("barcode", ""),
            qrcode=data.get("qrcode"),
            rfid=data.get("rfid"),
            name=data.get("name", ""),
            sku=data.get("sku", ""),
            category=data.get("category", ""),
            location=data.get("location", ""),
            quantity=data.get("quantity", 0),
            price=data.get("price", 0.0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
