"""Tests for ProductService."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, MagicMock

import pytest
from bson import ObjectId

from app.core.services.product_service import ProductService


pytestmark = pytest.mark.anyio


def _product_dict(oid=None, name="Test", barcode="123", quantity=0, price=0.0):
    return {
        "_id": oid or ObjectId(),
        "barcode": barcode, "qrcode": None, "rfid": None,
        "name": name, "sku": "S1",
        "category": "", "location": "",
        "quantity": quantity, "price": price,
        "weight": 0.0, "height": 0.0, "width": 0.0, "length": 0.0,
        "images": [],
        "created_at": None, "updated_at": None,
    }


class TestProductService:
    @pytest.fixture
    def repo(self):
        return AsyncMock(
            add=AsyncMock(return_value=ObjectId()),
            get_one=AsyncMock(),
            get_many=AsyncMock(return_value=[]),
            update=AsyncMock(),
            delete=AsyncMock(return_value=True),
            count=AsyncMock(return_value=0),
        )

    @pytest.fixture
    def service(self, repo):
        return ProductService(product_repo=repo)

    @pytest.fixture
    def service_with_storage(self, repo):
        storage = MagicMock()
        storage.put_object = Mock()
        storage.generate_presigned_url = Mock(return_value="https://example.com/img.jpg")
        storage.delete_file = Mock()
        validator = MagicMock()
        return ProductService(product_repo=repo, storage=storage, image_validator=validator)

    async def test_create(self, repo, service):
        oid = ObjectId("507f1f77bcf86cd799439011")
        repo.add.return_value = oid
        repo.get_one.return_value = _product_dict(oid=oid, name="Test", barcode="123",
                                                   quantity=0, price=10.0)
        product = await service.create(
            name="Test", sku="S1", barcode="123",
            category="C", location="L", price=10.0,
        )
        assert product.barcode == "123"
        repo.add.assert_awaited_once()

    async def test_get_by_id_found(self, repo, service):
        oid = ObjectId()
        repo.get_one.return_value = _product_dict(oid=oid, name="Test")
        product = await service.get_by_id(str(oid))
        assert product is not None
        assert product.name == "Test"

    async def test_get_by_id_not_found(self, repo, service):
        repo.get_one.return_value = None
        product = await service.get_by_id("507f1f77bcf86cd799439011")
        assert product is None

    async def test_find_by_code_found(self, repo, service):
        repo.get_one.return_value = _product_dict(barcode="123")
        product = await service.find_by_code("123")
        assert product is not None
        assert product.barcode == "123"

    async def test_find_by_code_not_found(self, repo, service):
        repo.get_one.return_value = None
        product = await service.find_by_code("nonexistent")
        assert product is None

    async def test_update(self, repo, service):
        oid = ObjectId()
        repo.get_one.return_value = _product_dict(oid=oid, name="Updated", quantity=5)
        product = await service.update(str(oid), name="Updated")
        assert product is not None
        assert product.name == "Updated"
        repo.update.assert_awaited_once()

    async def test_delete(self, repo, service):
        result = await service.delete("507f1f77bcf86cd799439011")
        assert result is True
        repo.delete.assert_awaited_once()

    async def test_increase_quantity(self, repo, service):
        oid = ObjectId()
        repo.get_one.side_effect = [
            _product_dict(oid=oid, name="Test", quantity=5),
            _product_dict(oid=oid, name="Test", quantity=8),
        ]
        product = await service.increase_quantity(str(oid), 3)
        assert product is not None
        assert product.quantity == 8

    async def test_increase_quantity_product_not_found(self, repo, service):
        repo.get_one.return_value = None
        product = await service.increase_quantity("507f1f77bcf86cd799439011", 3)
        assert product is None

    async def test_set_quantity(self, repo, service):
        oid = ObjectId()
        repo.get_one.return_value = _product_dict(oid=oid, name="Test", quantity=20)
        product = await service.set_quantity(str(oid), 20)
        assert product is not None
        assert product.quantity == 20

    async def test_search(self, repo, service):
        repo.get_many.return_value = [_product_dict(name="Test")]
        results = await service.search("Test")
        assert len(results) == 1
        assert results[0].name == "Test"

    async def test_get_all_returns_tuple(self, repo, service):
        repo.get_many.return_value = [
            _product_dict(name="A", barcode="1"),
            _product_dict(name="B", barcode="2"),
        ]
        repo.count.return_value = 2
        results, total = await service.get_all(limit=10, skip=0)
        assert len(results) == 2
        assert total == 2

    async def test_get_all_filtered_by_category(self, repo, service):
        repo.get_many.return_value = [_product_dict(name="CatProduct", barcode="1")]
        repo.count.return_value = 1
        results, total = await service.get_all(limit=10, skip=0, category="Electronics")
        assert len(results) == 1
        assert total == 1
        call_args, call_kwargs = repo.get_many.call_args
        assert call_args[0]["category"] == "Electronics"

    async def test_get_all_filtered_by_price(self, repo, service):
        repo.get_many.return_value = [_product_dict(name="P", barcode="1", price=50)]
        repo.count.return_value = 1
        results, total = await service.get_all(limit=10, skip=0, min_price=10, max_price=100)
        assert len(results) == 1
        call_args, _ = repo.get_many.call_args
        assert call_args[0]["price"]["$gte"] == 10
        assert call_args[0]["price"]["$lte"] == 100

    async def test_get_all_sorted(self, repo, service):
        repo.get_many.return_value = []
        repo.count.return_value = 0
        await service.get_all(limit=10, skip=0, sort_by="price", sort_order="desc")
        _, call_kwargs = repo.get_many.call_args
        assert call_kwargs["sort"] == [("price", -1)]

    async def test_get_categories(self, repo, service):
        repo.get_many.return_value = [
            {"category": "A"},
            {"category": "B"},
            {"category": "A"},
            {"category": ""},
        ]
        cats = await service.get_categories()
        assert sorted(cats) == ["A", "B"]

    async def test_upload_image(self, repo, service_with_storage):
        oid = ObjectId()
        repo.get_one.return_value = _product_dict(oid=oid)
        repo.add.return_value = oid
        repo.update = AsyncMock()

        mock_file = MagicMock()
        mock_file.filename = "test.jpg"
        mock_file.read = AsyncMock(return_value=b"fake-image-data")

        result = await service_with_storage.upload_image(
            product_id=str(oid),
            file=mock_file,
        )
        assert result["filename"] == "test.jpg"
        assert "id" in result
        assert "object_key" in result
        repo.update.assert_awaited_once()

    async def test_get_images(self, repo, service_with_storage):
        oid = ObjectId()
        repo.get_one.return_value = _product_dict(oid=oid,
            name="Test", barcode="1")
        repo.get_one.return_value["images"] = [
            {"id": "img1", "filename": "test.jpg", "object_key": "products/oid/img1.jpg", "uploaded_at": "2024-01-01"},
        ]

        images = await service_with_storage.get_images(str(oid))
        assert len(images) == 1
        assert images[0]["url"] == "https://example.com/img.jpg"
        service_with_storage._storage.generate_presigned_url.assert_called_once()

    async def test_delete_image(self, repo, service_with_storage):
        oid = ObjectId()
        repo.get_one.return_value = _product_dict(oid=oid,
            name="Test", barcode="1")
        repo.get_one.return_value["images"] = [
            {"id": "img1", "filename": "test.jpg", "object_key": "products/oid/img1.jpg", "uploaded_at": "2024-01-01"},
        ]
        repo.update = AsyncMock()

        result = await service_with_storage.delete_image(str(oid), "img1")
        assert result is True
        service_with_storage._storage.delete_file.assert_called_once_with("products/oid/img1.jpg")
        repo.update.assert_awaited_once()

    async def test_delete_image_not_found(self, repo, service_with_storage):
        oid = ObjectId()
        repo.get_one.return_value = _product_dict(oid=oid, name="Test")
        result = await service_with_storage.delete_image(str(oid), "nonexistent")
        assert result is False
