"""Сервис для работы с товарами."""

from datetime import datetime
from typing import Any

from bson import ObjectId

from app.adapters.repositories.abc_repo import RepositoryInterface
from app.adapters.repositories.product_repo import ProductRepo
from app.core.domain.models.product import Product


class ProductService:
    """Сервис товаров."""

    def __init__(self, product_repo: RepositoryInterface) -> None:
        """Инициализация."""
        self._repo = product_repo

    async def find_by_code(self, code: str) -> Product | None:
        """Найти товар по коду (barcode/qrcode/rfid)."""
        data = await self._repo.get_one(
            {
                "$or": [
                    {"barcode": code},
                    {"qrcode": code},
                    {"rfid": code},
                ]
            }
        )
        if not data:
            return None
        return Product.from_dict(data)

    async def get_by_id(self, product_id: str) -> Product | None:
        """Получить товар по ID."""
        data = await self._repo.get_one({"_id": ObjectId(product_id)})
        if not data:
            return None
        return Product.from_dict(data)

    async def create(
        self,
        name: str,
        sku: str,
        barcode: str,
        category: str = "",
        location: str = "",
        price: float = 0.0,
        qrcode: str | None = None,
        rfid: str | None = None,
    ) -> Product:
        """Создать товар."""
        now = datetime.utcnow()
        data = {
            "name": name,
            "sku": sku,
            "barcode": barcode,
            "qrcode": qrcode,
            "rfid": rfid,
            "category": category,
            "location": location,
            "quantity": 0,
            "price": price,
            "created_at": now,
            "updated_at": now,
        }
        id = await self._repo.add(data)
        product = await self._repo.get_one({"_id": id})
        return Product.from_dict(product)

    async def update(self, product_id: str, **kwargs) -> Product | None:
        """Обновить товар."""
        kwargs["updated_at"] = datetime.utcnow()
        await self._repo.update({"_id": ObjectId(product_id)}, {"$set": kwargs})
        return await self.get_by_id(product_id)

    async def delete(self, product_id: str) -> bool:
        """Удалить товар."""
        return await self._repo.delete({"_id": ObjectId(product_id)})

    async def increase_quantity(self, product_id: str, quantity: int) -> Product | None:
        """Увеличить количество товара."""
        product = await self.get_by_id(product_id)
        if not product:
            return None
        new_qty = product.quantity + quantity
        return await self.update(product_id, quantity=new_qty)

    async def set_quantity(self, product_id: str, quantity: int) -> Product | None:
        """Установить количество товара."""
        return await self.update(product_id, quantity=quantity)

    async def search(self, query: str, limit: int = 20) -> list[Product]:
        """Поиск товаров."""
        results = await self._repo.get_many(
            {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"sku": {"$regex": query, "$options": "i"}},
                    {"barcode": {"$regex": query, "$options": "i"}},
                ]
            },
            limit=limit,
        )
        return [Product.from_dict(r) for r in results]

    async def get_all(self, limit: int = 100, skip: int = 0) -> list[Product]:
        """Получить все товары."""
        results = await self._repo.get_many({}, limit=limit, skip=skip)
        return [Product.from_dict(r) for r in results]
