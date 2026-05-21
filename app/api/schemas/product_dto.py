"""DTO для товаров."""

from dataclasses import dataclass, field
from datetime import datetime

from app.core.domain.models.product import Product


@dataclass
class ProductSearchDTO:
    """Поиск товара."""

    code: str


@dataclass
class ProductImageDTO:
    """Изображение товара."""

    id: str
    filename: str
    url: str
    uploaded_at: str


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
    created_at: str | None = None
    updated_at: str | None = None
    weight: float = 0.0
    height: float = 0.0
    width: float = 0.0
    length: float = 0.0
    images: list[ProductImageDTO] = field(default_factory=list)

    @classmethod
    def from_product(cls, product: Product, presigned_urls: dict[str, str] | None = None) -> "ProductDTO":
        """Из модели Product."""
        urls = presigned_urls or {}
        images = [
            ProductImageDTO(
                id=img["id"],
                filename=img["filename"],
                url=urls.get(img["id"], ""),
                uploaded_at=img.get("uploaded_at", ""),
            )
            for img in product.images
        ]
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
            weight=product.weight,
            height=product.height,
            width=product.width,
            length=product.length,
            images=images,
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
    weight: float = 0.0
    height: float = 0.0
    width: float = 0.0
    length: float = 0.0
    qrcode: str | None = None
    rfid: str | None = None


@dataclass
class ProductCellDTO:
    """Ячейка с товаром (для результата поиска)."""

    warehouse_id: str
    warehouse_name: str
    cell_id: str
    cell_code: str
    quantity: int
    capacity: int


@dataclass
class ProductSearchResultDTO:
    """Результат поиска товара по названию."""

    product: ProductDTO
    cells: list[ProductCellDTO]


@dataclass
class ProductListDTO:
    """Список товаров."""

    items: list[ProductDTO]
    total: int
