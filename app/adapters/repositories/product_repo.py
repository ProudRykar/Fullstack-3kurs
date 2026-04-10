"""Репозиторий для товаров."""

from app.adapters.interfaces.db import DBGatewayInterface
from app.adapters.repositories.mongo_repo import MongoRepo


class ProductRepo(MongoRepo):
    """Репозиторий товаров."""

    def __init__(self, gateway: DBGatewayInterface) -> None:
        """Инициализация."""
        super().__init__(gateway, collection_name="products")

    async def find_by_code(self, code: str) -> dict | None:
        """Поиск товара по штрихкоду, QR-коду или RFID.

        Args:
            code: barcode, qrcode или rfid

        Returns:
            dict | None: Товар или None
        """
        collection = await self._init_collection()
        result = await collection.find_one(
            {
                "$or": [
                    {"barcode": code},
                    {"qrcode": code},
                    {"rfid": code},
                ]
            }
        )
        return result

    async def find_by_barcode(self, barcode: str) -> dict | None:
        """Поиск по штрихкоду."""
        collection = await self._init_collection()
        return await collection.find_one({"barcode": barcode})

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        """Поиск по названию или артикулу."""
        collection = await self._init_collection()
        cursor = collection.find(
            {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"sku": {"$regex": query, "$options": "i"}},
                    {"barcode": {"$regex": query, "$options": "i"}},
                ]
            }
        ).limit(limit)
        return await cursor.to_list()
