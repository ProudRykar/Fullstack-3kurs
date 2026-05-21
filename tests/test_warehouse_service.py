"""Tests for WarehouseService."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from bson import ObjectId

from app.core.domain.models.warehouse_cell import WarehouseCell
from app.core.errors.warehouse import WarehouseCapacityError


pytestmark = pytest.mark.anyio


def _wh_dict(oid=None, name="Main", location="Warehouse", cell_count=0, capacity_per_cell=0):
    return {
        "_id": oid or ObjectId(),
        "name": name,
        "location": location,
        "cell_count": cell_count,
        "capacity_per_cell": capacity_per_cell,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def _cell_dict(oid=None, warehouse_id="w1", code="1", capacity=100,
               product_id=None, product_name=None, product_barcode=None, quantity=0):
    return {
        "_id": oid or ObjectId(),
        "warehouse_id": warehouse_id,
        "code": code,
        "capacity": capacity,
        "product_id": product_id,
        "product_name": product_name,
        "product_barcode": product_barcode,
        "quantity": quantity,
        "updated_at": datetime.utcnow(),
    }


class TestWarehouseService:
    @pytest.fixture
    def warehouse_repo(self):
        return AsyncMock(
            add=AsyncMock(return_value=ObjectId()),
            get_one=AsyncMock(),
            get_many=AsyncMock(return_value=[]),
            update=AsyncMock(),
            delete=AsyncMock(return_value=True),
        )

    @pytest.fixture
    def cell_repo(self):
        return AsyncMock(
            add=AsyncMock(return_value=ObjectId()),
            get_one=AsyncMock(),
            get_many=AsyncMock(return_value=[]),
            update=AsyncMock(),
            update_many=AsyncMock(return_value=1),
            delete=AsyncMock(return_value=True),
        )

    @pytest.fixture
    def service(self, warehouse_repo, cell_repo):
        from app.core.services.warehouse_service import WarehouseService
        return WarehouseService(
            warehouse_repo=warehouse_repo,
            cell_repo=cell_repo,
        )

    # ── Warehouse CRUD ──────────────────────────────────────────────

    async def test_create_without_cells(self, warehouse_repo, service):
        oid = ObjectId()
        warehouse_repo.add.return_value = oid
        warehouse_repo.get_one.return_value = _wh_dict(oid=oid, name="Main")
        wh = await service.create(name="Main", location="Here")
        assert wh.name == "Main"
        warehouse_repo.add.assert_awaited_once()

    async def test_create_with_cells(self, warehouse_repo, cell_repo, service):
        oid = ObjectId()
        warehouse_repo.add.return_value = oid
        warehouse_repo.get_one.return_value = _wh_dict(oid=oid, name="Main", cell_count=3, capacity_per_cell=100)
        cell_repo.get_many.return_value = []
        wh = await service.create(name="Main", location="Here", cell_count=3, capacity_per_cell=100)
        assert wh.name == "Main"
        assert cell_repo.add.await_count == 3

    async def test_get_by_id_found(self, warehouse_repo, service):
        oid = ObjectId()
        warehouse_repo.get_one.return_value = _wh_dict(oid=oid)
        wh = await service.get_by_id(str(oid))
        assert wh is not None
        assert wh.name == "Main"

    async def test_get_by_id_not_found(self, warehouse_repo, service):
        warehouse_repo.get_one.return_value = None
        wh = await service.get_by_id("507f1f77bcf86cd799439011")
        assert wh is None

    async def test_get_all(self, warehouse_repo, service):
        warehouse_repo.get_many.return_value = [_wh_dict()]
        results = await service.get_all()
        assert len(results) == 1

    async def test_update(self, warehouse_repo, cell_repo, service):
        oid = ObjectId()
        warehouse_repo.get_one.side_effect = [
            _wh_dict(oid=oid, cell_count=5, capacity_per_cell=100),
            _wh_dict(oid=oid, name="Updated", location="NewLoc",
                     cell_count=5, capacity_per_cell=100),
        ]
        wh = await service.update(str(oid), name="Updated", location="NewLoc",
                                  cell_count=5, capacity_per_cell=100)
        assert wh is not None
        assert wh.name == "Updated"
        warehouse_repo.update.assert_awaited_once()

    async def test_update_raises_capacity_error(self, warehouse_repo, service):
        oid = ObjectId()
        warehouse_repo.get_one.return_value = _wh_dict(oid=oid, cell_count=10, capacity_per_cell=100)
        with pytest.raises(WarehouseCapacityError):
            await service.update(str(oid), name="Test", location="Loc", cell_count=5, capacity_per_cell=50)

    async def test_delete(self, cell_repo, service):
        result = await service.delete("507f1f77bcf86cd799439011")
        assert result is True
        cell_repo.delete.assert_awaited_once_with({"warehouse_id": "507f1f77bcf86cd799439011"})

    # ── Cell operations ────────────────────────────────────────────

    async def test_create_cell(self, cell_repo, service):
        oid = ObjectId()
        cell_repo.add.return_value = oid
        cell_repo.get_one.return_value = _cell_dict(oid=oid, warehouse_id="w1", code="A1", capacity=100)
        cell = await service.create_cell("w1", "A1", 100)
        assert cell.code == "A1"
        assert cell.capacity == 100

    async def test_get_cells(self, cell_repo, service):
        cell_repo.get_many.return_value = [_cell_dict()]
        cells = await service.get_cells("w1")
        assert len(cells) == 1

    async def test_get_empty_cells(self, cell_repo, service):
        cell_repo.get_many.return_value = [_cell_dict()]
        cells = await service.get_empty_cells("w1")
        assert len(cells) == 1

    async def test_place_product_in_empty_cell(self, cell_repo, service):
        oid = ObjectId()
        cell_repo.get_one.side_effect = [
            _cell_dict(oid=oid, product_id=None),
            _cell_dict(oid=oid, product_id="p1", product_name="Box",
                       product_barcode="123", quantity=10),
        ]
        cell = await service.place_product_in_cell(str(oid), "p1", "Box", "123", 10)
        assert cell is not None
        assert cell.product_id == "p1"
        assert cell.quantity == 10

    async def test_place_product_in_occupied_cell(self, cell_repo, service):
        oid = ObjectId()
        cell_repo.get_one.side_effect = [
            _cell_dict(oid=oid, product_id="p1", product_name="Box",
                       product_barcode="123", quantity=5, capacity=100),
            _cell_dict(oid=oid, product_id="p1", product_name="Box",
                       product_barcode="123", quantity=8, capacity=100),
        ]
        cell = await service.place_product_in_cell(str(oid), "p1", "Box", "123", 3)
        assert cell is not None
        assert cell.quantity == 8

    async def test_place_product_over_capacity(self, cell_repo, service):
        oid = ObjectId()
        cell_repo.get_one.side_effect = [
            _cell_dict(oid=oid, product_id="p1", product_name="Box",
                       product_barcode="123", quantity=95, capacity=100),
        ]
        cell = await service.place_product_in_cell(str(oid), "p1", "Box", "123", 10)
        assert cell is None

    async def test_remove_product_from_cell(self, cell_repo, service):
        oid = ObjectId()
        cell_repo.get_one.return_value = _cell_dict(oid=oid, product_id=None, product_name=None,
                                                    product_barcode=None, quantity=0)
        cell = await service.remove_product_from_cell(str(oid))
        assert cell is not None
        assert cell.product_id is None
        assert cell.quantity == 0

    async def test_delete_cell(self, cell_repo, service):
        result = await service.delete_cell("507f1f77bcf86cd799439011")
        assert result is True

    # ── Search methods ─────────────────────────────────────────────

    async def test_find_product_cell_found(self, cell_repo, service):
        cell_repo.get_many.return_value = [_cell_dict(product_barcode="123")]
        cell = await service.find_product_cell("w1", "123")
        assert cell is not None

    async def test_find_product_cell_not_found(self, cell_repo, service):
        cell_repo.get_many.return_value = []
        cell = await service.find_product_cell("w1", "999")
        assert cell is None

    async def test_find_product_in_warehouse_found(self, cell_repo, service):
        cell_repo.get_many.return_value = [_cell_dict(product_barcode="123")]
        cell = await service.find_product_in_warehouse("w1", "123")
        assert cell is not None

    async def test_get_product_cell_info(self, cell_repo, service):
        cell_repo.get_many.return_value = [_cell_dict(product_barcode="123", quantity=10, capacity=100)]
        info = await service.get_product_cell_info("w1", "123")
        assert info is not None
        assert info["cell_quantity"] == 10

    async def test_get_product_cell_info_not_found(self, cell_repo, service):
        cell_repo.get_many.return_value = []
        info = await service.get_product_cell_info("w1", "999")
        assert info is None

    async def test_find_cells_by_barcode(self, warehouse_repo, cell_repo, service):
        wh_oid = ObjectId()
        cell_repo.get_many.return_value = [_cell_dict(warehouse_id=str(wh_oid), product_barcode="123")]
        warehouse_repo.get_one.return_value = {"_id": wh_oid, "name": "Main"}
        results = await service.find_cells_by_barcode("123")
        assert len(results) == 1
        assert results[0]["warehouse_name"] == "Main"

    async def test_find_cells_by_barcode_no_cells(self, cell_repo, service):
        cell_repo.get_many.return_value = []
        results = await service.find_cells_by_barcode("999")
        assert results == []

    async def test_get_cell_by_code_found(self, cell_repo, service):
        cell_repo.get_one.return_value = _cell_dict(code="A1")
        cell = await service.get_cell_by_code("w1", "A1")
        assert cell is not None
        assert cell.code == "A1"

    async def test_get_cell_by_code_not_found(self, cell_repo, service):
        cell_repo.get_one.return_value = None
        cell = await service.get_cell_by_code("w1", "ZZ")
        assert cell is None

    # ── Auto-assign ────────────────────────────────────────────────

    async def test_auto_assign_cell_existing_not_full(self, cell_repo, service):
        oid = ObjectId()
        cell_repo.get_many.return_value = [
            _cell_dict(oid=oid, warehouse_id="w1", code="1", product_id="p1",
                       product_name="Box", product_barcode="123", quantity=5, capacity=100),
        ]
        cell_repo.get_one.side_effect = [
            _cell_dict(oid=oid, warehouse_id="w1", code="1", product_id="p1",
                       product_name="Box", product_barcode="123", quantity=5, capacity=100),
            _cell_dict(oid=oid, warehouse_id="w1", code="1", product_id="p1",
                       product_name="Box", product_barcode="123", quantity=8, capacity=100),
        ]
        cell = await service.auto_assign_cell("w1", "p1", "Box", "123", 3)
        assert cell is not None
        assert cell.quantity == 8

    async def test_auto_assign_cell_existing_full(self, cell_repo, service):
        oid_full = ObjectId()
        oid_empty = ObjectId()
        cell_repo.get_many.return_value = [
            _cell_dict(oid=oid_full, warehouse_id="w1", code="1", product_id="p1",
                       product_name="Box", product_barcode="123", quantity=100, capacity=100),
            _cell_dict(oid=oid_empty, warehouse_id="w1", code="2", product_id=None,
                       product_name=None, product_barcode=None, quantity=0, capacity=100),
        ]
        cell_repo.get_one.side_effect = [
            _cell_dict(oid=oid_empty, warehouse_id="w1", code="2", product_id=None,
                       product_name=None, product_barcode=None, quantity=0, capacity=100),
            _cell_dict(oid=oid_empty, warehouse_id="w1", code="2", product_id="p1",
                       product_name="Box", product_barcode="123", quantity=3, capacity=100),
        ]
        cell = await service.auto_assign_cell("w1", "p1", "Box", "123", 3)
        assert cell is not None
        assert cell.code == "2"

    async def test_auto_assign_cell_new_product(self, cell_repo, service):
        oid = ObjectId()
        cell_repo.get_many.return_value = [
            _cell_dict(oid=oid, warehouse_id="w1", code="1", product_id=None,
                       product_name=None, product_barcode=None, quantity=0, capacity=100),
        ]
        cell_repo.get_one.side_effect = [
            _cell_dict(oid=oid, warehouse_id="w1", code="1", product_id=None,
                       product_name=None, product_barcode=None, quantity=0, capacity=100),
            _cell_dict(oid=oid, warehouse_id="w1", code="1", product_id="p1",
                       product_name="Box", product_barcode="123", quantity=3, capacity=100),
        ]
        cell = await service.auto_assign_cell("w1", "p1", "Box", "123", 3)
        assert cell is not None
        assert cell.code == "1"

    async def test_auto_assign_cell_no_space(self, cell_repo, service):
        cell_repo.get_many.return_value = []
        cell = await service.auto_assign_cell("w1", "p1", "Box", "123", 3)
        assert cell is None

    # ── Suggest cell ──────────────────────────────────────────────

    async def test_suggest_cell_existing(self, cell_repo, service):
        cell_repo.get_many.return_value = [
            _cell_dict(warehouse_id="w1", code="1", product_id="p1",
                       product_barcode="123", quantity=5, capacity=100),
        ]
        suggestion = await service.suggest_cell("w1", "123")
        assert suggestion is not None
        assert suggestion["cell_code"] == "1"

    async def test_suggest_cell_empty(self, cell_repo, service):
        cell_repo.get_many.return_value = [
            _cell_dict(warehouse_id="w1", code="1", product_id=None,
                       product_name=None, product_barcode=None, quantity=0, capacity=100),
        ]
        suggestion = await service.suggest_cell("w1", "new")
        assert suggestion is not None
        assert suggestion["cell_code"] == "1"

    async def test_suggest_cell_no_space(self, cell_repo, service):
        cell_repo.get_many.return_value = []
        suggestion = await service.suggest_cell("w1", "123")
        assert suggestion is None
