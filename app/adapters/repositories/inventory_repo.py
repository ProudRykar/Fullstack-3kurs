"""Репозиторий для инвентаризаций."""

from app.adapters.interfaces.db import DBGatewayInterface
from app.adapters.repositories.mongo_repo import MongoRepo


class InventoryRepo(MongoRepo):
    """Репозиторий инвентаризаций."""

    def __init__(self, gateway: DBGatewayInterface) -> None:
        super().__init__(gateway, collection_name="inventory")

    async def find_by_number(self, number: str) -> dict | None:
        collection = await self._init_collection()
        return await collection.find_one({"number": number})

    async def get_by_status(self, status: str, limit: int = 50) -> list[dict]:
        collection = await self._init_collection()
        cursor = collection.find({"status": status}).sort("date", -1).limit(limit)
        return await cursor.to_list()

    async def get_all(self, limit: int = 50, skip: int = 0) -> list[dict]:
        collection = await self._init_collection()
        cursor = collection.find({}).sort("date", -1).limit(limit).skip(skip)
        return await cursor.to_list()
