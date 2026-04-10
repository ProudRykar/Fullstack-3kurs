"""DTO для товаров."""

from dataclasses import dataclass
from typing import Any

from app.core.domain.models.product import Product


@dataclass
class ProductSearchDTO:
    """Поиск товара."""

    code: str


@dataclass
class ProductDTO:
    """Товар (ответ)."""

    id: str
    barcode: str
    qrcode: str | None
    rfid: str | None
    name: str
    sku: str
    category: str
    location: str
    quantity: int
    price: float
    created_at: str | None
    updated_at: str | None

    @classmethod
    def from_product(cls, product: Product) -> "ProductDTO":
        """Из модели Product."""
        return cls(
            id=str(product._id) if product._id else "",
            barcode=product.barcode,
            qrcode=product.qrcode,
            rfid=product.rfid,
            name=product.name,
            sku=product.sku,
            category=product.category,
            location=product.location,
            quantity=product.quantity,
            price=product.price,
            created_at=product.created_at.isoformat() if product.created_at else None,
            updated_at=product.updated_at.isoformat() if product.updated_at else None,
        )


@dataclass
class ProductCreateDTO:
    """Создание/обновление товара."""

    name: str
    sku: str
    barcode: str
    category: str = ""
    location: str = ""
    quantity: int = 0
    price: float = 0.0
    qrcode: str | None = None
    rfid: str | None = None


@dataclass
class ProductListDTO:
    """Список товаров."""

    items: list[ProductDTO]
    total: int
