"""Tests for InventoryService."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from bson import ObjectId

from app.core.services.inventory_service import InventoryService


pytestmark = pytest.mark.anyio


def _inv_dict(oid=None, number="INV-00001", status="in_progress", scans=None):
    return {
        "_id": oid or ObjectId(),
        "number": number,
        "date": datetime.utcnow(),
        "scans": scans or [],
        "status": status,
        "created_by": "user1",
        "warehouse_id": "w1",
    }


def _product_dict(oid=None, barcode="123", name="Test", quantity=10):
    return {
        "_id": oid or ObjectId(),
        "barcode": barcode, "qrcode": None, "rfid": None,
        "name": name, "sku": "S1",
        "category": "", "location": "",
        "quantity": quantity, "price": 0.0,
        "weight": 0.0, "height": 0.0, "width": 0.0, "length": 0.0,
        "created_at": None, "updated_at": None,
    }


def _scan_dict(product_id, barcode="123", product_name="Test", db_qty=10, scanned_qty=5):
    return {
        "product_id": product_id,
        "product_name": product_name,
        "barcode": barcode,
        "db_quantity": db_qty,
        "scanned_quantity": scanned_qty,
    }


class TestInventoryService:
    @pytest.fixture
    def inventory_repo(self):
        return AsyncMock(
            add=AsyncMock(return_value=ObjectId()),
            get_one=AsyncMock(),
            get_many=AsyncMock(return_value=[]),
            update=AsyncMock(),
            delete=AsyncMock(return_value=True),
            _init_collection=AsyncMock(),
        )

    @pytest.fixture
    def product_repo(self):
        return AsyncMock(
            get_one=AsyncMock(),
        )

    @pytest.fixture
    def product_service(self, product_repo):
        from app.core.services.product_service import ProductService
        return ProductService(product_repo=product_repo)

    @pytest.fixture
    def service(self, inventory_repo, product_service):
        return InventoryService(
            inventory_repo=inventory_repo,
            product_service=product_service,
        )

    async def test_create(self, inventory_repo, service):
        oid = ObjectId()
        inventory_repo.add.return_value = oid
        inventory_repo.get_one.return_value = _inv_dict(oid=oid)
        inv = await service.create(created_by="user1", warehouse_id="w1")
        assert inv.status == "in_progress"
        assert inv.created_by == "user1"
        inventory_repo.add.assert_awaited_once()

    async def test_get_by_id_found(self, inventory_repo, service):
        oid = ObjectId()
        inventory_repo.get_one.return_value = _inv_dict(oid=oid)
        inv = await service.get_by_id(str(oid))
        assert inv is not None
        assert inv.status == "in_progress"

    async def test_get_by_id_not_found(self, inventory_repo, service):
        inventory_repo.get_one.return_value = None
        inv = await service.get_by_id("507f1f77bcf86cd799439011")
        assert inv is None

    async def test_scan_new_product(self, inventory_repo, product_repo, service):
        inv_oid = ObjectId()
        prod_oid = ObjectId()
        inventory_repo.get_one.side_effect = [
            _inv_dict(oid=inv_oid, scans=[]),
            _inv_dict(oid=inv_oid, scans=[
                _scan_dict(str(prod_oid), barcode="123", db_qty=10, scanned_qty=5),
            ]),
        ]
        product_repo.get_one.return_value = _product_dict(oid=prod_oid, barcode="123", quantity=10)

        inv = await service.scan(str(inv_oid), "123", 5)
        assert inv is not None
        assert len(inv.scans) == 1
        assert inv.scans[0].scanned_quantity == 5
        inventory_repo.update.assert_awaited_once()

    async def test_scan_existing_product(self, inventory_repo, product_repo, service):
        inv_oid = ObjectId()
        prod_oid = ObjectId()
        product_repo.get_one.return_value = _product_dict(oid=prod_oid, barcode="123", quantity=10)

        inventory_repo.get_one.side_effect = [
            _inv_dict(oid=inv_oid, scans=[
                _scan_dict(str(prod_oid), barcode="123", db_qty=10, scanned_qty=5),
            ]),
            _inv_dict(oid=inv_oid, scans=[
                _scan_dict(str(prod_oid), barcode="123", db_qty=10, scanned_qty=8),
            ]),
        ]

        inv = await service.scan(str(inv_oid), "123", 8)
        assert inv is not None
        assert len(inv.scans) == 1
        assert inv.scans[0].scanned_quantity == 8

    async def test_scan_inventory_not_found(self, inventory_repo, service):
        inventory_repo.get_one.return_value = None
        inv = await service.scan("507f1f77bcf86cd799439011", "123", 5)
        assert inv is None

    async def test_scan_inventory_not_in_progress(self, inventory_repo, service):
        oid = ObjectId()
        inventory_repo.get_one.return_value = _inv_dict(oid=oid, status="completed")
        inv = await service.scan(str(oid), "123", 5)
        assert inv is None

    async def test_scan_product_not_found(self, inventory_repo, product_repo, service):
        oid = ObjectId()
        inventory_repo.get_one.return_value = _inv_dict(oid=oid, scans=[])
        product_repo.get_one.return_value = None
        inv = await service.scan(str(oid), "nonexistent", 5)
        assert inv is None

    async def test_complete(self, inventory_repo, service):
        oid = ObjectId()
        inventory_repo.get_one.side_effect = [
            _inv_dict(oid=oid),
            _inv_dict(oid=oid, status="completed"),
        ]
        inv = await service.complete(str(oid))
        assert inv is not None
        assert inv.status == "completed"
        inventory_repo.update.assert_awaited_once()

    async def test_complete_not_in_progress(self, inventory_repo, service):
        oid = ObjectId()
        inventory_repo.get_one.return_value = _inv_dict(oid=oid, status="completed")
        inv = await service.complete(str(oid))
        assert inv is None

    async def test_get_all(self, inventory_repo, service):
        inventory_repo.get_many.return_value = [_inv_dict()]
        results = await service.get_all()
        assert len(results) == 1

    async def test_get_all_filtered_by_warehouse(self, inventory_repo, service):
        inventory_repo.get_many.return_value = [_inv_dict()]
        results = await service.get_all(warehouse_id="w1")
        assert len(results) == 1

    async def test_get_active_found(self, inventory_repo, service):
        oid = ObjectId()
        inventory_repo.get_many.return_value = [_inv_dict(oid=oid)]
        inv = await service.get_active()
        assert inv is not None
        assert inv.status == "in_progress"

    async def test_get_active_not_found(self, inventory_repo, service):
        inventory_repo.get_many.return_value = []
        inv = await service.get_active()
        assert inv is None

    async def test_get_active_filtered_by_warehouse(self, inventory_repo, service):
        inventory_repo.get_many.return_value = [_inv_dict()]
        inv = await service.get_active(warehouse_id="w1")
        assert inv is not None
