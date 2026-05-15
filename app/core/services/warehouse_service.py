"""Сервис для работы со складами."""

from datetime import datetime

from bson import ObjectId

from app.adapters.repositories.abc_repo import RepositoryInterface
from app.adapters.repositories.warehouse_repo import WarehouseCellRepo, WarehouseRepo
from app.core.domain.models.warehouse import Warehouse
from app.core.domain.models.warehouse_cell import WarehouseCell


class WarehouseService:
    def __init__(
        self,
        warehouse_repo: RepositoryInterface,
        cell_repo: RepositoryInterface,
    ) -> None:
        self._repo = warehouse_repo
        self._cell_repo = cell_repo

    async def create(self, name: str, location: str = "", cell_count: int = 0, capacity_per_cell: int = 0) -> Warehouse:
        now = datetime.utcnow()
        data = {
            "name": name, "location": location,
            "cell_count": cell_count, "capacity_per_cell": capacity_per_cell,
            "created_at": now, "updated_at": now,
        }
        id = await self._repo.add(data)
        result = await self._repo.get_one({"_id": id})

        if cell_count > 0:
            await self._sync_cells(str(id), cell_count, capacity_per_cell)

        return Warehouse.from_dict(result)

    async def get_by_id(self, warehouse_id: str) -> Warehouse | None:
        data = await self._repo.get_one({"_id": ObjectId(warehouse_id)})
        if not data:
            return None
        return Warehouse.from_dict(data)

    async def get_all(self) -> list[Warehouse]:
        results = await self._repo.get_many({})
        return [Warehouse.from_dict(r) for r in results]

    async def update(self, warehouse_id: str, name: str, location: str, cell_count: int = 0, capacity_per_cell: int = 0) -> Warehouse | None:
        await self._repo.update(
            {"_id": ObjectId(warehouse_id)},
            {
                "$set": {
                    "name": name, "location": location,
                    "cell_count": cell_count, "capacity_per_cell": capacity_per_cell,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if cell_count > 0:
            await self._sync_cells(warehouse_id, cell_count, capacity_per_cell)

        return await self.get_by_id(warehouse_id)

    async def delete(self, warehouse_id: str) -> bool:
        await self._cell_repo.delete({"warehouse_id": warehouse_id})
        return await self._repo.delete({"_id": ObjectId(warehouse_id)})

    async def _sync_cells(self, warehouse_id: str, target_count: int, capacity: int) -> None:
        existing = await self._cell_repo.get_many({"warehouse_id": warehouse_id})
        existing_count = len(existing)
        existing_codes = {c.get("code") for c in existing}

        if target_count > existing_count:
            for i in range(existing_count + 1, target_count + 1):
                code = str(i)
                if code not in existing_codes:
                    await self._cell_repo.add({
                        "warehouse_id": warehouse_id,
                        "code": code,
                        "capacity": capacity,
                        "product_id": None,
                        "product_name": None,
                        "product_barcode": None,
                        "quantity": 0,
                        "updated_at": datetime.utcnow(),
                    })
        elif target_count < existing_count:
            to_delete = sorted(existing, key=lambda c: int(c.get("code", "0")) if c.get("code", "").isdigit() else 999999)
            for cell in to_delete[target_count:]:
                if cell.get("product_id") is None:
                    await self._cell_repo.delete({"_id": cell["_id"]})

        if capacity > 0:
            await self._cell_repo.update(
                {"warehouse_id": warehouse_id, "capacity": {"$ne": capacity}},
                {"$set": {"capacity": capacity}},
            )

    async def create_cell(self, warehouse_id: str, code: str, capacity: int = 0) -> WarehouseCell:
        data = {
            "warehouse_id": warehouse_id,
            "code": code,
            "capacity": capacity,
            "product_id": None,
            "product_name": None,
            "product_barcode": None,
            "quantity": 0,
            "updated_at": datetime.utcnow(),
        }
        id = await self._cell_repo.add(data)
        result = await self._cell_repo.get_one({"_id": id})
        return WarehouseCell.from_dict(result)

    async def get_cells(self, warehouse_id: str) -> list[WarehouseCell]:
        results = await self._cell_repo.get_many({"warehouse_id": warehouse_id})
        return [WarehouseCell.from_dict(r) for r in results]

    async def get_empty_cells(self, warehouse_id: str) -> list[WarehouseCell]:
        results = await self._cell_repo.get_many(
            {"warehouse_id": warehouse_id, "product_id": None}
        )
        return [WarehouseCell.from_dict(r) for r in results]

    async def place_product_in_cell(
        self, cell_id: str, product_id: str, product_name: str, product_barcode: str, quantity: int
    ) -> WarehouseCell | None:
        cell = await self._cell_repo.get_one({"_id": ObjectId(cell_id)})
        if not cell:
            return None

        if cell.get("product_id") is None:
            await self._cell_repo.update(
                {"_id": ObjectId(cell_id)},
                {
                    "$set": {
                        "product_id": product_id,
                        "product_name": product_name,
                        "product_barcode": product_barcode,
                        "quantity": quantity,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
        else:
            capacity = cell.get("capacity", 0)
            curr_qty = cell.get("quantity", 0)
            new_qty = curr_qty + quantity
            if capacity > 0 and new_qty > capacity:
                return None
            await self._cell_repo.update(
                {"_id": ObjectId(cell_id)},
                {"$set": {"quantity": new_qty, "updated_at": datetime.utcnow()}},
            )

        result = await self._cell_repo.get_one({"_id": ObjectId(cell_id)})
        return WarehouseCell.from_dict(result)

    async def remove_product_from_cell(self, cell_id: str) -> WarehouseCell | None:
        await self._cell_repo.update(
            {"_id": ObjectId(cell_id)},
            {
                "$set": {
                    "product_id": None,
                    "product_name": None,
                    "product_barcode": None,
                    "quantity": 0,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        result = await self._cell_repo.get_one({"_id": ObjectId(cell_id)})
        return WarehouseCell.from_dict(result)

    async def delete_cell(self, cell_id: str) -> bool:
        return await self._cell_repo.delete({"_id": ObjectId(cell_id)})

    async def find_product_cell(self, warehouse_id: str, product_barcode: str) -> WarehouseCell | None:
        results = await self._cell_repo.get_many(
            {"warehouse_id": warehouse_id, "product_barcode": product_barcode}
        )
        if not results:
            return None
        return WarehouseCell.from_dict(results[0])

    async def find_product_in_warehouse(self, warehouse_id: str, product_barcode: str) -> WarehouseCell | None:
        results = await self._cell_repo.get_many(
            {"warehouse_id": warehouse_id, "product_barcode": product_barcode}
        )
        if not results:
            return None
        return WarehouseCell.from_dict(results[0])

    async def auto_assign_cell(self, warehouse_id: str, product_id: str, product_name: str, product_barcode: str, quantity: int) -> WarehouseCell | None:
        cells_map = await self.get_cells_map(warehouse_id)
        existing = next((c for c in cells_map.values() if c.product_barcode == product_barcode), None)

        if existing:
            if not existing.is_full:
                return await self.place_product_in_cell(
                    existing.id, product_id, product_name, product_barcode, quantity
                )
            start = int(existing.code) if existing.code.isdigit() else 0
            nearby = await self._find_nearby_cell(cells_map, start, product_barcode, needed=quantity)
            if nearby:
                return await self.place_product_in_cell(
                    nearby.id, product_id, product_name, product_barcode, quantity
                )
            return None

        empty_sorted = sorted(
            [c for c in cells_map.values() if c.is_empty],
            key=lambda c: int(c.code) if c.code.isdigit() else 999999
        )
        if empty_sorted:
            return await self.place_product_in_cell(
                empty_sorted[0].id, product_id, product_name, product_barcode, quantity
            )

        return None

    async def get_product_cell_info(self, warehouse_id: str, product_barcode: str) -> dict | None:
        cell = await self.find_product_in_warehouse(warehouse_id, product_barcode)
        if not cell:
            return None
        return {
            "cell_id": cell.id,
            "cell_code": cell.code,
            "cell_quantity": cell.quantity,
            "cell_capacity": cell.capacity,
        }

    async def find_cells_by_barcode(self, barcode: str) -> list[dict]:
        """Найти все ячейки с товаром по штрихкоду (по всем складам)."""
        cells = await self._cell_repo.get_many({"product_barcode": barcode})
        if not cells:
            return []

        warehouse_ids = set(c.get("warehouse_id") for c in cells)
        warehouses = {}
        for wid in warehouse_ids:
            w = await self._repo.get_one({"_id": ObjectId(wid)})
            if w:
                warehouses[wid] = w.get("name", "")

        result = []
        for c in cells:
            cell = WarehouseCell.from_dict(c)
            result.append({
                "warehouse_id": cell.warehouse_id,
                "warehouse_name": warehouses.get(cell.warehouse_id, ""),
                "cell_id": cell.id,
                "cell_code": cell.code,
                "quantity": cell.quantity,
                "capacity": cell.capacity,
            })
        return result

    async def get_cell_by_code(self, warehouse_id: str, code: str) -> WarehouseCell | None:
        result = await self._cell_repo.get_one({"warehouse_id": warehouse_id, "code": code})
        if not result:
            return None
        return WarehouseCell.from_dict(result)

    async def get_cells_map(self, warehouse_id: str) -> dict[str, WarehouseCell]:
        results = await self._cell_repo.get_many({"warehouse_id": warehouse_id})
        return {c.get("code"): WarehouseCell.from_dict(c) for c in results}

    async def _find_nearby_cell(self, cells_map: dict[str, WarehouseCell], start_code: int, product_barcode: str, needed: int = 0) -> WarehouseCell | None:
        for delta in range(1, 1000):
            for candidate in (start_code + delta, start_code - delta):
                if candidate <= 0:
                    continue
                cell = cells_map.get(str(candidate))
                if not cell:
                    continue
                if cell.is_empty:
                    return cell
                if cell.product_barcode == product_barcode and not cell.is_full and (cell.quantity + needed) <= cell.capacity:
                    return cell
        return None

    async def suggest_cell(self, warehouse_id: str, product_barcode: str, pending_quantity: int = 0) -> dict | None:
        cells_map = await self.get_cells_map(warehouse_id)
        existing = next((c for c in cells_map.values() if c.product_barcode == product_barcode), None)

        if existing:
            effective_qty = existing.quantity + pending_quantity
            if effective_qty < existing.capacity:
                return {
                    "cell_id": existing.id,
                    "cell_code": existing.code,
                    "cell_quantity": existing.quantity,
                    "cell_capacity": existing.capacity,
                    "available_space": existing.capacity - effective_qty,
                }
            start = int(existing.code) if existing.code.isdigit() else 0
            nearby = await self._find_nearby_cell(cells_map, start, product_barcode, pending_quantity)
            if nearby:
                return {
                    "cell_id": nearby.id,
                    "cell_code": nearby.code,
                    "cell_quantity": nearby.quantity,
                    "cell_capacity": nearby.capacity,
                    "available_space": nearby.available_space,
                }
            return None

        empty_sorted = sorted(
            [c for c in cells_map.values() if c.is_empty],
            key=lambda c: int(c.code) if c.code.isdigit() else 999999
        )
        if empty_sorted:
            cell = empty_sorted[0]
            return {
                "cell_id": cell.id,
                "cell_code": cell.code,
                "cell_quantity": 0,
                "cell_capacity": cell.capacity,
                "available_space": cell.capacity,
            }

        return None

    async def get_items_cell_info(self, warehouse_id: str, items: list[dict]) -> list[dict]:
        cells_map = await self.get_cells_map(warehouse_id)
        cell_occupancy: dict[str, int] = {}
        cell_product: dict[str, str] = {}
        result = []

        for item in items:
            barcode = item["barcode"]
            qty = item.get("quantity", 1)

            target_cell = None
            for c in cells_map.values():
                assigned_barcode = c.product_barcode if c.product_barcode else cell_product.get(c.code)
                if assigned_barcode == barcode:
                    occupied = cell_occupancy.get(c.code, 0)
                    base_qty = c.quantity if c.product_barcode == barcode else 0
                    if base_qty + occupied + qty <= c.capacity:
                        target_cell = c
                        break

            if not target_cell:
                for c in cells_map.values():
                    assigned_barcode = c.product_barcode if c.product_barcode else cell_product.get(c.code)
                    if assigned_barcode == barcode:
                        occupied = cell_occupancy.get(c.code, 0)
                        base_qty = c.quantity if c.product_barcode == barcode else 0
                        start = int(c.code) if c.code.isdigit() else 0
                        nearby = self._find_nearby_cell_sync(cells_map, cell_occupancy, cell_product, start, barcode, base_qty + occupied + qty)
                        if nearby:
                            target_cell = nearby
                            break
                    if target_cell:
                        break

            if not target_cell:
                empty_sorted = sorted(
                    [c for c in cells_map.values() if c.is_empty and c.code not in cell_product],
                    key=lambda c: int(c.code) if c.code.isdigit() else 999999
                )
                if empty_sorted:
                    target_cell = empty_sorted[0]

            if target_cell:
                occupied = cell_occupancy.get(target_cell.code, 0)
                base_qty = target_cell.quantity if target_cell.product_barcode == barcode else 0
                new_qty = base_qty + occupied + qty
                cell_occupancy[target_cell.code] = occupied + qty
                cell_product[target_cell.code] = barcode
                result.append({
                    "cell_code": target_cell.code,
                    "cell_quantity": new_qty,
                    "cell_capacity": target_cell.capacity,
                })
            else:
                result.append(None)

        return result

    def _find_nearby_cell_sync(self, cells_map: dict[str, WarehouseCell], cell_occupancy: dict[str, int], cell_product: dict[str, str], start_code: int, product_barcode: str, needed: int) -> WarehouseCell | None:
        for delta in range(1, 1000):
            for candidate in (start_code + delta, start_code - delta):
                if candidate <= 0:
                    continue
                cell = cells_map.get(str(candidate))
                if not cell:
                    continue
                if cell.code in cell_product and cell_product[cell.code] != product_barcode:
                    continue
                occupied = cell_occupancy.get(cell.code, 0)
                base = cell.quantity if cell.product_barcode == product_barcode else 0
                if cell.is_empty and cell.code not in cell_product:
                    return cell
                if cell.product_barcode == product_barcode and not cell.is_full and base + occupied + needed <= cell.capacity:
                    return cell
        return None
