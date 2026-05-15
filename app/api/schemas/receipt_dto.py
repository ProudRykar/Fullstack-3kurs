"""DTO для приёмок."""

from dataclasses import dataclass

from app.core.domain.models.receipt import Receipt, ReceiptItem


@dataclass
class ReceiptItemDTO:
    """Элемент приёмки."""

    product_id: str
    product_name: str
    barcode: str
    quantity: int
    price: float

    @classmethod
    def from_item(cls, item: ReceiptItem) -> "ReceiptItemDTO":
        return cls(
            product_id=item.product_id,
            product_name=item.product_name,
            barcode=item.barcode,
            quantity=item.quantity,
            price=item.price,
        )


@dataclass
class ReceiptDTO:
    """Приёмка."""

    id: str
    number: str
    date: str | None
    items: list[ReceiptItemDTO]
    status: str
    created_by: str
    confirmed_at: str | None
    total: float
    total_quantity: int

    @classmethod
    def from_receipt(cls, receipt: Receipt) -> "ReceiptDTO":
        return cls(
            id=str(receipt._id) if receipt._id else "",
            number=receipt.number,
            date=receipt.date.isoformat() if receipt.date else None,
            items=[ReceiptItemDTO.from_item(i) for i in receipt.items],
            status=receipt.status,
            created_by=receipt.created_by,
            confirmed_at=receipt.confirmed_at.isoformat()
            if receipt.confirmed_at
            else None,
            total=receipt.total,
            total_quantity=receipt.total_quantity,
        )


@dataclass
class ReceiptCreateItemDTO:
    """Добавить товар в приёмку."""

    barcode: str
    quantity: int


@dataclass
class ReceiptListDTO:
    """Список приёмок."""

    items: list[ReceiptDTO]
    total: int
