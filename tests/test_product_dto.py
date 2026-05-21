"""Tests for Product DTOs: ProductDTO, ProductCreateDTO, ProductListDTO, ProductCellDTO, ProductSearchResultDTO."""

from datetime import datetime

from bson import ObjectId

from app.api.schemas.product_dto import (
    ProductCellDTO,
    ProductCreateDTO,
    ProductDTO,
    ProductListDTO,
    ProductSearchResultDTO,
)
from app.core.domain.models.product import Product


class TestProductDTO:
    def test_from_product_with_oid(self):
        now = datetime.utcnow()
        p = Product(_id=ObjectId("507f1f77bcf86cd799439011"), barcode="123", name="Test",
                     sku="S1", category="C", location="L", quantity=5, price=10.0,
                     weight=1.5, height=2.0, width=3.0, length=4.0,
                     created_at=now, updated_at=now)
        dto = ProductDTO.from_product(p)
        assert dto.id == "507f1f77bcf86cd799439011"
        assert dto.barcode == "123"
        assert dto.name == "Test"
        assert dto.weight == 1.5
        assert dto.height == 2.0
        assert dto.width == 3.0
        assert dto.length == 4.0
        assert dto.created_at is not None
        assert dto.updated_at is not None

    def test_from_product_without_oid(self):
        p = Product(barcode="123", name="Test", sku="S1")
        dto = ProductDTO.from_product(p)
        assert dto.id == ""
        assert dto.created_at is None

    def test_from_product_without_dates(self):
        p = Product(_id=ObjectId(), barcode="123", name="Test")
        dto = ProductDTO.from_product(p)
        assert dto.created_at is None
        assert dto.updated_at is None


class TestProductCreateDTO:
    def test_defaults(self):
        dto = ProductCreateDTO(name="Test", sku="S1", barcode="123")
        assert dto.category == ""
        assert dto.quantity == 0
        assert dto.price == 0.0
        assert dto.weight == 0.0
        assert dto.height == 0.0
        assert dto.width == 0.0
        assert dto.length == 0.0
        assert dto.qrcode is None
        assert dto.rfid is None


class TestProductCellDTO:
    def test_fields(self):
        dto = ProductCellDTO(warehouse_id="w1", warehouse_name="Main",
                              cell_id="c1", cell_code="A1", quantity=10, capacity=100)
        assert dto.warehouse_id == "w1"
        assert dto.cell_code == "A1"
        assert dto.quantity == 10
        assert dto.capacity == 100


class TestProductSearchResultDTO:
    def test_fields(self):
        p = ProductDTO(id="p1", barcode="123", qrcode=None, rfid=None, name="Test",
                        sku="S1", category="C", location="L", quantity=5, price=10.0)
        cells = [ProductCellDTO(warehouse_id="w1", warehouse_name="Main",
                                cell_id="c1", cell_code="A1", quantity=10, capacity=100)]
        dto = ProductSearchResultDTO(product=p, cells=cells)
        assert dto.product.name == "Test"
        assert len(dto.cells) == 1
        assert dto.cells[0].cell_code == "A1"


class TestProductListDTO:
    def test_fields(self):
        items = [
            ProductDTO(id="p1", barcode="123", qrcode=None, rfid=None, name="A",
                       sku="S1", category="C", location="L", quantity=1, price=10.0),
            ProductDTO(id="p2", barcode="456", qrcode=None, rfid=None, name="B",
                       sku="S2", category="C", location="L", quantity=2, price=20.0),
        ]
        dto = ProductListDTO(items=items, total=2)
        assert len(dto.items) == 2
        assert dto.total == 2
