"""Tests for ReceiptService."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from bson import ObjectId

from app.core.domain.models.receipt import Receipt
from app.core.services.receipt_service import ReceiptService


pytestmark = pytest.mark.anyio


def _product_dict(oid=None, barcode="123", name="Test", quantity=10, price=100.0):
    return {
        "_id": oid or ObjectId(),
        "barcode": barcode, "qrcode": None, "rfid": None,
        "name": name, "sku": "S1",
        "category": "C", "location": "L",
        "quantity": quantity, "price": price,
        "weight": 1.0, "height": 1.0, "width": 1.0, "length": 1.0,
        "created_at": None, "updated_at": None,
    }


def _receipt_dict(oid=None, number="PR-00001", status="draft", items=None):
    return {
        "_id": oid or ObjectId(),
        "number": number,
        "date": datetime.utcnow(),
        "items": items or [],
        "status": status,
        "created_by": "user1",
        "confirmed_at": None,
        "warehouse_id": "w1",
    }


class TestReceiptService:
    @pytest.fixture
    def receipt_repo(self):
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
    def warehouse_service(self):
        return AsyncMock(
            auto_assign_cell=AsyncMock(return_value=AsyncMock(code="A1")),
        )

    @pytest.fixture
    def service(self, receipt_repo, product_service, warehouse_service):
        return ReceiptService(
            receipt_repo=receipt_repo,
            product_service=product_service,
            warehouse_service=warehouse_service,
        )

    @pytest.fixture
    def service_no_wh(self, receipt_repo, product_service):
        return ReceiptService(
            receipt_repo=receipt_repo,
            product_service=product_service,
            warehouse_service=None,
        )

    async def test_create(self, receipt_repo, service):
        oid = ObjectId()
        receipt_repo.add.return_value = oid
        receipt_repo.get_one.return_value = _receipt_dict(oid=oid)
        receipt = await service.create(created_by="user1", warehouse_id="w1")
        assert receipt.number is not None
        assert receipt.status == "draft"
        assert receipt.created_by == "user1"
        receipt_repo.add.assert_awaited_once()

    async def test_get_by_id_found(self, receipt_repo, service):
        oid = ObjectId()
        receipt_repo.get_one.return_value = _receipt_dict(oid=oid)
        receipt = await service.get_by_id(str(oid))
        assert receipt is not None
        assert receipt.status == "draft"

    async def test_get_by_id_not_found(self, receipt_repo, service):
        receipt_repo.get_one.return_value = None
        receipt = await service.get_by_id("507f1f77bcf86cd799439011")
        assert receipt is None

    async def test_add_item(self, receipt_repo, product_repo, service):
        r_oid = ObjectId()
        p_oid = ObjectId()
        receipt_repo.get_one.side_effect = [
            _receipt_dict(oid=r_oid, items=[]),
            _receipt_dict(oid=r_oid, items=[
                {"product_id": str(p_oid), "product_name": "Test",
                 "barcode": "123", "quantity": 5, "price": 100.0, "cell_code": ""},
            ]),
        ]
        product_repo.get_one.return_value = _product_dict(oid=p_oid, barcode="123", price=100.0)

        receipt = await service.add_item(str(r_oid), str(p_oid), 5)
        assert receipt is not None
        assert len(receipt.items) == 1
        assert receipt.items[0].quantity == 5
        receipt_repo.update.assert_awaited_once()

    async def test_add_item_receipt_not_found(self, receipt_repo, service):
        receipt_repo.get_one.return_value = None
        receipt = await service.add_item("507f1f77bcf86cd799439011", str(ObjectId()), 5)
        assert receipt is None

    async def test_add_item_receipt_not_draft(self, receipt_repo, service):
        oid = ObjectId()
        receipt_repo.get_one.return_value = _receipt_dict(oid=oid, status="confirmed")
        receipt = await service.add_item(str(oid), str(ObjectId()), 5)
        assert receipt is None

    async def test_add_item_product_not_found(self, receipt_repo, product_repo, service):
        oid = ObjectId()
        receipt_repo.get_one.return_value = _receipt_dict(oid=oid)
        product_repo.get_one.return_value = None
        receipt = await service.add_item(str(oid), str(ObjectId()), 5)
        assert receipt is None

    async def test_remove_item(self, receipt_repo, service):
        oid = ObjectId()
        receipt_repo.get_one.side_effect = [
            _receipt_dict(oid=oid, items=[
                {"product_id": "p1", "product_name": "A", "barcode": "1",
                 "quantity": 2, "price": 10.0, "cell_code": ""},
            ]),
            _receipt_dict(oid=oid, items=[]),
        ]
        receipt = await service.remove_item(str(oid), 0)
        assert receipt is not None
        assert len(receipt.items) == 0

    async def test_remove_item_invalid_index(self, receipt_repo, service):
        oid = ObjectId()
        receipt_repo.get_one.side_effect = [
            _receipt_dict(oid=oid, items=[]),
            _receipt_dict(oid=oid, items=[]),
        ]
        receipt = await service.remove_item(str(oid), 0)
        assert receipt is not None
        receipt_repo.update.assert_not_called()

    async def test_confirm(self, receipt_repo, product_repo, service):
        r_oid = ObjectId()
        p_oid = ObjectId()
        now = datetime.utcnow()
        product_repo.get_one.return_value = _product_dict(oid=p_oid, quantity=10)

        receipt_repo.get_one.side_effect = [
            _receipt_dict(oid=r_oid, items=[
                {"product_id": str(p_oid), "product_name": "Test",
                 "barcode": "123", "quantity": 5, "price": 100.0, "cell_code": ""},
            ]),
            {**_receipt_dict(oid=r_oid, status="confirmed", items=[
                {"product_id": str(p_oid), "product_name": "Test",
                 "barcode": "123", "quantity": 5, "price": 100.0, "cell_code": "A1"},
            ]), "confirmed_at": now},
        ]

        receipt = await service.confirm(str(r_oid))
        assert receipt is not None
        assert receipt.status == "confirmed"
        assert receipt.confirmed_at is not None
        receipt_repo.update.assert_awaited_once()

    async def test_confirm_no_warehouse(self, receipt_repo, product_repo, service_no_wh):
        r_oid = ObjectId()
        p_oid = ObjectId()
        product_repo.get_one.return_value = _product_dict(oid=p_oid, quantity=10)

        receipt_repo.get_one.side_effect = [
            _receipt_dict(oid=r_oid, items=[
                {"product_id": str(p_oid), "product_name": "Test",
                 "barcode": "123", "quantity": 5, "price": 100.0, "cell_code": ""},
            ]),
            _receipt_dict(oid=r_oid, status="confirmed", items=[
                {"product_id": str(p_oid), "product_name": "Test",
                 "barcode": "123", "quantity": 5, "price": 100.0, "cell_code": ""},
            ]),
        ]

        receipt = await service_no_wh.confirm(str(r_oid))
        assert receipt is not None
        assert receipt.status == "confirmed"

    async def test_confirm_not_draft(self, receipt_repo, service):
        oid = ObjectId()
        receipt_repo.get_one.return_value = _receipt_dict(oid=oid, status="confirmed")
        receipt = await service.confirm(str(oid))
        assert receipt is None

    async def test_cancel(self, receipt_repo, service):
        oid = ObjectId()
        receipt_repo.get_one.side_effect = [
            _receipt_dict(oid=oid, items=[]),
            _receipt_dict(oid=oid, status="cancelled", items=[]),
        ]
        receipt = await service.cancel(str(oid))
        assert receipt is not None
        assert receipt.status == "cancelled"
        receipt_repo.update.assert_awaited_once()

    async def test_cancel_not_draft(self, receipt_repo, service):
        oid = ObjectId()
        receipt_repo.get_one.return_value = _receipt_dict(oid=oid, status="confirmed")
        receipt = await service.cancel(str(oid))
        assert receipt is None

    async def test_get_all(self, receipt_repo, service):
        receipt_repo.get_many.return_value = [_receipt_dict()]
        results = await service.get_all()
        assert len(results) == 1

    async def test_get_all_filtered_by_warehouse(self, receipt_repo, service):
        receipt_repo.get_many.return_value = [_receipt_dict()]
        results = await service.get_all(warehouse_id="w1")
        assert len(results) == 1

    async def test_get_drafts(self, receipt_repo, service):
        receipt_repo.get_by_status = AsyncMock(return_value=[_receipt_dict()])
        results = await service.get_drafts()
        assert len(results) == 1
