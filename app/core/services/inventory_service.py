"""Сервис для работы с инвентаризацией."""

from datetime import datetime
from typing import Any

from bson import ObjectId

from app.adapters.repositories.abc_repo import RepositoryInterface
from app.adapters.repositories.inventory_repo import InventoryRepo
from app.core.domain.models.inventory import Inventory, InventoryScan
from app.core.services.product_service import ProductService


class InventoryService:
    """Сервис инвентаризации."""

    def __init__(
        self,
        inventory_repo: RepositoryInterface,
        product_service: ProductService,
    ) -> None:
        self._repo = inventory_repo
        self._products = product_service

    async def _generate_number(self) -> str:
        collection = await self._repo._init_collection()
        count = await collection.count_documents({})
        return f"ИНВ-{str(count + 1).zfill(5)}"

    async def create(self, created_by: str) -> Inventory:
        now = datetime.utcnow()
        number = await self._generate_number()

        data = {
            "number": number,
            "date": now,
            "scans": [],
            "status": "in_progress",
            "created_by": created_by,
        }

        id = await self._repo.add(data)
        inv = await self._repo.get_one({"_id": id})
        return Inventory.from_dict(inv)

    async def get_by_id(self, inventory_id: str) -> Inventory | None:
        data = await self._repo.get_one({"_id": ObjectId(inventory_id)})
        if not data:
            return None
        return Inventory.from_dict(data)

    async def scan(
        self,
        inventory_id: str,
        barcode: str,
        scanned_quantity: int,
    ) -> Inventory | None:
        """Сканировать товар."""
        inventory = await self.get_by_id(inventory_id)
        if not inventory or inventory.status != "in_progress":
            return None

        product = await self._products.find_by_code(barcode)
        if not product:
            return None

        existing_index = next(
            (i for i, s in enumerate(inventory.scans) if s.barcode == barcode),
            None,
        )

        if existing_index is not None:
            inventory.scans[existing_index].scanned_quantity = scanned_quantity
        else:
            scan = InventoryScan(
                product_id=product.id,
                product_name=product.name,
                barcode=product.barcode,
                db_quantity=product.quantity,
                scanned_quantity=scanned_quantity,
            )
            inventory.scans.append(scan)

        await self._repo.update(
            {"_id": ObjectId(inventory_id)},
            {"$set": {"scans": [s.to_dict() for s in inventory.scans]}},
        )

        return await self.get_by_id(inventory_id)

    async def complete(self, inventory_id: str) -> Inventory | None:
        """Завершить инвентаризацию."""
        inventory = await self.get_by_id(inventory_id)
        if not inventory or inventory.status != "in_progress":
            return None

        inventory.status = "completed"

        await self._repo.update(
            {"_id": ObjectId(inventory_id)},
            {"$set": {"status": "completed"}},
        )

        return await self.get_by_id(inventory_id)

    async def get_all(self, limit: int = 50, skip: int = 0) -> list[Inventory]:
        results = await self._repo.get_many({}, limit=limit, skip=skip)
        return [Inventory.from_dict(r) for r in results]

    async def get_active(self) -> Inventory | None:
        results = await self._repo.get_by_status("in_progress", 1)
        if not results:
            return None
        return Inventory.from_dict(results[0])
