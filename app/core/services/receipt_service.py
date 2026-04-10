"""Сервис для работы с приёмками."""

from datetime import datetime
from typing import Any

from bson import ObjectId

from app.adapters.repositories.abc_repo import RepositoryInterface
from app.adapters.repositories.receipt_repo import ReceiptRepo
from app.core.domain.models.receipt import Receipt, ReceiptItem
from app.core.services.product_service import ProductService


class ReceiptService:
    """Сервис приёмок."""

    def __init__(
        self,
        receipt_repo: RepositoryInterface,
        product_service: ProductService,
    ) -> None:
        self._repo = receipt_repo
        self._products = product_service

    async def _generate_number(self) -> str:
        """Генерация номера приёмки."""
        collection = await self._repo._init_collection()
        count = await collection.count_documents({})
        return f"ПР-{str(count + 1).zfill(5)}"

    async def create(self, created_by: str) -> Receipt:
        """Создать новую приёмку."""
        now = datetime.utcnow()
        number = await self._generate_number()

        data = {
            "number": number,
            "date": now,
            "items": [],
            "status": "draft",
            "created_by": created_by,
            "confirmed_at": None,
        }

        id = await self._repo.add(data)
        receipt = await self._repo.get_one({"_id": id})
        return Receipt.from_dict(receipt)

    async def get_by_id(self, receipt_id: str) -> Receipt | None:
        """Получить приёмку по ID."""
        data = await self._repo.get_one({"_id": ObjectId(receipt_id)})
        if not data:
            return None
        return Receipt.from_dict(data)

    async def add_item(
        self,
        receipt_id: str,
        product_id: str,
        quantity: int,
        price: float,
    ) -> Receipt | None:
        """Добавить товар в приёмку."""
        receipt = await self.get_by_id(receipt_id)
        if not receipt or receipt.status != "draft":
            return None

        product = await self._products.get_by_id(product_id)
        if not product:
            return None

        item = ReceiptItem(
            product_id=product_id,
            product_name=product.name,
            barcode=product.barcode,
            quantity=quantity,
            price=price,
        )

        receipt.items.append(item)

        await self._repo.update(
            {"_id": ObjectId(receipt_id)},
            {"$set": {"items": [i.to_dict() for i in receipt.items]}},
        )

        return await self.get_by_id(receipt_id)

    async def remove_item(self, receipt_id: str, item_index: int) -> Receipt | None:
        """Удалить товар из приёмки."""
        receipt = await self.get_by_id(receipt_id)
        if not receipt or receipt.status != "draft":
            return None

        if 0 <= item_index < len(receipt.items):
            receipt.items.pop(item_index)
            await self._repo.update(
                {"_id": ObjectId(receipt_id)},
                {"$set": {"items": [i.to_dict() for i in receipt.items]}},
            )

        return await self.get_by_id(receipt_id)

    async def confirm(self, receipt_id: str) -> Receipt | None:
        """Подтвердить приёмк�� (увеличить количество товаров)."""
        receipt = await self.get_by_id(receipt_id)
        if not receipt or receipt.status != "draft":
            return None

        for item in receipt.items:
            await self._products.increase_quantity(item.product_id, item.quantity)

        receipt.status = "confirmed"
        receipt.confirmed_at = datetime.utcnow()

        await self._repo.update(
            {"_id": ObjectId(receipt_id)},
            {"$set": {"status": "confirmed", "confirmed_at": receipt.confirmed_at}},
        )

        return await self.get_by_id(receipt_id)

    async def cancel(self, receipt_id: str) -> Receipt | None:
        """Отменить приёмку."""
        receipt = await self.get_by_id(receipt_id)
        if not receipt or receipt.status != "draft":
            return None

        await self._repo.update(
            {"_id": ObjectId(receipt_id)},
            {"$set": {"status": "cancelled"}},
        )

        return await self.get_by_id(receipt_id)

    async def get_all(self, limit: int = 50, skip: int = 0) -> list[Receipt]:
        """Получить все приёмки."""
        results = await self._repo.get_many({}, limit=limit, skip=skip)
        return [Receipt.from_dict(r) for r in results]

    async def get_drafts(self, limit: int = 20) -> list[Receipt]:
        """Получить черновики."""
        results = await self._repo.get_by_status("draft", limit)
        return [Receipt.from_dict(r) for r in results]
