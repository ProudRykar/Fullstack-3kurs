"""Tests for all domain models: Product, Receipt, Inventory, Warehouse, WarehouseCell, Role, Permission, TokenClaims."""

import pytest
from bson import ObjectId
from datetime import datetime

from app.core.domain.models.product import Product
from app.core.domain.models.receipt import Receipt, ReceiptItem
from app.core.domain.models.inventory import Inventory, InventoryScan
from app.core.domain.models.warehouse import Warehouse
from app.core.domain.models.warehouse_cell import WarehouseCell
from app.core.domain.models.role import Role
from app.core.domain.models.permission import Permission, ROLE_PERMISSIONS
from app.core.domain.models.token import TokenClaims


# ── Product ──────────────────────────────────────────────────────────────

class TestProduct:
    def test_id_property_with_oid(self):
        oid = ObjectId()
        p = Product(_id=oid)
        assert p.id == str(oid)

    def test_id_property_none(self):
        p = Product()
        assert p.id == ""

    def test_id_property_stable(self):
        oid = ObjectId()
        p = Product(_id=oid)
        assert p.id == p.id

    def test_to_dict_includes_all_fields(self):
        now = datetime.utcnow()
        p = Product(_id=ObjectId(), barcode="123", name="Test", sku="SKU1",
                     category="Cat", location="Loc", quantity=5, price=10.0,
                     weight=1.5, height=2.0, width=3.0, length=4.0,
                     created_at=now, updated_at=now)
        d = p.to_dict()
        assert d["barcode"] == "123"
        assert d["name"] == "Test"
        assert d["weight"] == 1.5
        assert d["height"] == 2.0
        assert d["width"] == 3.0
        assert d["length"] == 4.0

    def test_from_dict_roundtrip(self):
        oid = ObjectId()
        now = datetime.utcnow()
        data = {
            "_id": oid, "barcode": "123", "name": "Test", "sku": "S1",
            "category": "C", "location": "L", "quantity": 10, "price": 99.0,
            "weight": 1.0, "height": 2.0, "width": 3.0, "length": 4.0,
            "created_at": now, "updated_at": now,
        }
        p = Product.from_dict(data)
        assert p._id == oid
        assert p.barcode == "123"
        assert p.weight == 1.0
        assert p.length == 4.0

    def test_from_dict_defaults(self):
        p = Product.from_dict({})
        assert p.barcode == ""
        assert p.quantity == 0
        assert p.weight == 0
        assert p.created_at is None


# ── ReceiptItem ──────────────────────────────────────────────────────────

class TestReceiptItem:
    def test_to_dict(self):
        item = ReceiptItem(product_id="p1", product_name="Box", barcode="456",
                           quantity=3, price=50.0, cell_code="A1")
        d = item.to_dict()
        assert d["product_id"] == "p1"
        assert d["cell_code"] == "A1"

    def test_from_dict(self):
        item = ReceiptItem.from_dict({"product_id": "p1", "product_name": "Box",
                                       "barcode": "456", "quantity": 3, "price": 50.0})
        assert item.product_id == "p1"
        assert item.price == 50.0
        assert item.cell_code == ""

    def test_from_dict_defaults(self):
        item = ReceiptItem.from_dict({})
        assert item.product_id == ""
        assert item.quantity == 0


# ── Receipt ──────────────────────────────────────────────────────────────

class TestReceipt:
    def test_total(self):
        r = Receipt(items=[
            ReceiptItem(product_id="p1", product_name="A", barcode="1", quantity=2, price=10.0),
            ReceiptItem(product_id="p2", product_name="B", barcode="2", quantity=3, price=20.0),
        ])
        assert r.total == 2 * 10.0 + 3 * 20.0

    def test_total_empty(self):
        assert Receipt().total == 0.0

    def test_total_quantity(self):
        r = Receipt(items=[
            ReceiptItem(product_id="p1", product_name="A", barcode="1", quantity=5, price=1.0),
            ReceiptItem(product_id="p2", product_name="B", barcode="2", quantity=3, price=1.0),
        ])
        assert r.total_quantity == 8

    def test_to_dict_includes_items(self):
        r = Receipt(number="PR-001", status="draft", items=[
            ReceiptItem(product_id="p1", product_name="A", barcode="1", quantity=1, price=10.0),
        ])
        d = r.to_dict()
        assert d["number"] == "PR-001"
        assert len(d["items"]) == 1

    def test_from_dict(self):
        oid = ObjectId()
        now = datetime.utcnow()
        data = {
            "_id": oid, "number": "PR-001", "date": now, "status": "confirmed",
            "created_by": "user1", "warehouse_id": "w1",
            "items": [{"product_id": "p1", "product_name": "A", "barcode": "1",
                       "quantity": 2, "price": 10.0}],
        }
        r = Receipt.from_dict(data)
        assert r.number == "PR-001"
        assert r.status == "confirmed"
        assert len(r.items) == 1
        assert r.items[0].product_name == "A"

    def test_from_dict_defaults(self):
        r = Receipt.from_dict({})
        assert r.status == "draft"
        assert r.items == []


# ── InventoryScan ────────────────────────────────────────────────────────

class TestInventoryScan:
    def test_diff_positive(self):
        s = InventoryScan(product_id="p1", product_name="A", barcode="1",
                          db_quantity=5, scanned_quantity=8)
        assert s.diff == 3

    def test_diff_negative(self):
        s = InventoryScan(product_id="p1", product_name="A", barcode="1",
                          db_quantity=5, scanned_quantity=2)
        assert s.diff == -3

    def test_is_ok_true(self):
        s = InventoryScan(product_id="p1", product_name="A", barcode="1",
                          db_quantity=5, scanned_quantity=5)
        assert s.is_ok is True

    def test_is_ok_false(self):
        s = InventoryScan(product_id="p1", product_name="A", barcode="1",
                          db_quantity=5, scanned_quantity=6)
        assert s.is_ok is False

    def test_to_dict(self):
        s = InventoryScan(product_id="p1", product_name="A", barcode="1",
                          db_quantity=5, scanned_quantity=6)
        d = s.to_dict()
        assert d["db_quantity"] == 5
        assert d["scanned_quantity"] == 6

    def test_from_dict(self):
        s = InventoryScan.from_dict({"product_id": "p1", "product_name": "A",
                                      "barcode": "1", "db_quantity": 5, "scanned_quantity": 6})
        assert s.db_quantity == 5
        assert s.diff == 1

    def test_from_dict_defaults(self):
        s = InventoryScan.from_dict({})
        assert s.db_quantity == 0
        assert s.scanned_quantity == 0


# ── Inventory ────────────────────────────────────────────────────────────

class TestInventory:
    def test_total_checked(self):
        inv = Inventory(scans=[
            InventoryScan(product_id="p1", product_name="A", barcode="1", db_quantity=5, scanned_quantity=5),
            InventoryScan(product_id="p2", product_name="B", barcode="2", db_quantity=3, scanned_quantity=4),
        ])
        assert inv.total_checked == 2

    def test_total_diff(self):
        inv = Inventory(scans=[
            InventoryScan(product_id="p1", product_name="A", barcode="1", db_quantity=5, scanned_quantity=5),
            InventoryScan(product_id="p2", product_name="B", barcode="2", db_quantity=3, scanned_quantity=6),
        ])
        assert inv.total_diff == 3

    def test_diff_count(self):
        inv = Inventory(scans=[
            InventoryScan(product_id="p1", product_name="A", barcode="1", db_quantity=5, scanned_quantity=5),
            InventoryScan(product_id="p2", product_name="B", barcode="2", db_quantity=3, scanned_quantity=6),
            InventoryScan(product_id="p3", product_name="C", barcode="3", db_quantity=2, scanned_quantity=1),
        ])
        assert inv.diff_count == 2

    def test_from_dict(self):
        oid = ObjectId()
        data = {
            "_id": oid, "number": "INV-001", "status": "completed",
            "scans": [{"product_id": "p1", "product_name": "A", "barcode": "1",
                       "db_quantity": 5, "scanned_quantity": 5}],
        }
        inv = Inventory.from_dict(data)
        assert inv.number == "INV-001"
        assert inv.status == "completed"
        assert len(inv.scans) == 1

    def test_from_dict_defaults(self):
        inv = Inventory.from_dict({})
        assert inv.status == "in_progress"
        assert inv.scans == []


# ── Warehouse ────────────────────────────────────────────────────────────

class TestWarehouse:
    def test_id_property(self):
        oid = ObjectId()
        w = Warehouse(_id=oid)
        assert w.id == str(oid)

    def test_id_property_none(self):
        assert Warehouse().id == ""

    def test_to_dict(self):
        w = Warehouse(name="Main", location="Floor 1", cell_count=10, capacity_per_cell=100)
        d = w.to_dict()
        assert d["name"] == "Main"
        assert d["cell_count"] == 10

    def test_from_dict(self):
        oid = ObjectId()
        w = Warehouse.from_dict({"_id": oid, "name": "Main", "cell_count": 5})
        assert w._id == oid
        assert w.name == "Main"
        assert w.cell_count == 5

    def test_from_dict_defaults(self):
        w = Warehouse.from_dict({})
        assert w.name == ""
        assert w.cell_count == 0


# ── WarehouseCell ────────────────────────────────────────────────────────

class TestWarehouseCell:
    def test_id_property(self):
        oid = ObjectId()
        c = WarehouseCell(_id=oid)
        assert c.id == str(oid)

    def test_is_empty_true(self):
        assert WarehouseCell().is_empty is True

    def test_is_empty_false(self):
        c = WarehouseCell(product_id="p1", product_name="A", product_barcode="1")
        assert c.is_empty is False

    def test_is_full_empty(self):
        assert WarehouseCell().is_full is False

    def test_is_full_at_capacity(self):
        c = WarehouseCell(product_id="p1", product_name="A", product_barcode="1",
                          quantity=100, capacity=100)
        assert c.is_full is True

    def test_is_full_under_capacity(self):
        c = WarehouseCell(product_id="p1", product_name="A", product_barcode="1",
                          quantity=50, capacity=100)
        assert c.is_full is False

    def test_available_space_empty(self):
        c = WarehouseCell(capacity=100)
        assert c.available_space == 100

    def test_available_space_partial(self):
        c = WarehouseCell(product_id="p1", product_name="A", product_barcode="1",
                          quantity=40, capacity=100)
        assert c.available_space == 60

    def test_available_space_full(self):
        c = WarehouseCell(product_id="p1", product_name="A", product_barcode="1",
                          quantity=100, capacity=100)
        assert c.available_space == 0

    def test_available_space_no_capacity(self):
        c = WarehouseCell(product_id="p1", product_name="A", product_barcode="1",
                          quantity=50, capacity=0)
        assert c.available_space == 0

    def test_to_dict(self):
        c = WarehouseCell(warehouse_id="w1", code="A1", capacity=100,
                          product_id="p1", product_name="Box", product_barcode="123", quantity=10)
        d = c.to_dict()
        assert d["warehouse_id"] == "w1"
        assert d["code"] == "A1"
        assert d["quantity"] == 10

    def test_from_dict(self):
        oid = ObjectId()
        data = {"_id": oid, "warehouse_id": "w1", "code": "A1", "capacity": 100,
                "product_id": "p1", "product_name": "Box", "product_barcode": "123", "quantity": 10}
        c = WarehouseCell.from_dict(data)
        assert c._id == oid
        assert c.code == "A1"
        assert c.quantity == 10

    def test_from_dict_defaults(self):
        c = WarehouseCell.from_dict({})
        assert c.code == ""
        assert c.quantity == 0
        assert c.product_id is None


# ── Role ─────────────────────────────────────────────────────────────────

class TestRole:
    def test_values(self):
        assert Role.GUEST == "guest"
        assert Role.USER == "user"
        assert Role.ADMIN == "admin"

    def test_default(self):
        assert Role.default() == Role.USER


# ── Permission ───────────────────────────────────────────────────────────

class TestPermission:
    def test_values_exist(self):
        assert Permission.PRODUCT_VIEW == "product:view"
        assert Permission.USER_REGISTER == "user:register"

    def test_guest_permissions(self):
        perms = ROLE_PERMISSIONS["guest"]
        assert Permission.USER_REGISTER in perms
        assert Permission.USER_LOGIN in perms
        assert Permission.PRODUCT_VIEW not in perms

    def test_user_permissions(self):
        perms = ROLE_PERMISSIONS["user"]
        assert Permission.PRODUCT_VIEW in perms
        assert Permission.RECEIPT_CREATE in perms
        assert Permission.RECEIPT_CONFIRM not in perms
        assert Permission.USER_LIST not in perms

    def test_admin_permissions(self):
        perms = ROLE_PERMISSIONS["admin"]
        assert Permission.USER_LIST in perms
        assert Permission.RECEIPT_CONFIRM in perms
        assert Permission.INVENTORY_COMPLETE in perms
        assert Permission.WAREHOUSE_DELETE in perms

    def test_unknown_role_returns_empty(self):
        assert ROLE_PERMISSIONS.get("nonexistent", []) == []


# ── TokenClaims ──────────────────────────────────────────────────────────

class TestTokenClaims:
    def test_frozen(self):
        tc = TokenClaims(sub="user1", type="access", jti="abc123")
        with pytest.raises(AttributeError):
            tc.sub = "other"

    def test_defaults(self):
        tc = TokenClaims(sub="user1", type="refresh", jti="xyz")
        assert tc.username is None
        assert tc.email is None

    def test_claims_with_optional(self):
        tc = TokenClaims(sub="user1", type="access", jti="abc", username="john", email="john@test.com")
        assert tc.username == "john"
        assert tc.email == "john@test.com"
