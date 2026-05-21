"""Сервис для работы с товарами."""

import io
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from bson import ObjectId

from app.adapters.gateways.s3 import MinioGateway
from app.adapters.repositories.abc_repo import RepositoryInterface
from app.core.domain.models.product import Product
from app.core.services.validation_service import ImageValidator

if TYPE_CHECKING:
    from litestar.datastructures import UploadFile


class ProductService:
    """Сервис товаров."""

    def __init__(
        self,
        product_repo: RepositoryInterface,
        storage: MinioGateway | None = None,
        image_validator: ImageValidator | None = None,
    ) -> None:
        """Инициализация."""
        self._repo = product_repo
        self._storage = storage
        self._image_validator = image_validator

    async def find_by_code(self, code: str) -> Product | None:
        """Найти товар по коду (barcode/qrcode/rfid)."""
        data = await self._repo.get_one(
            {
                "$or": [
                    {"barcode": code},
                    {"qrcode": code},
                    {"rfid": code},
                ]
            }
        )
        if not data:
            return None
        return Product.from_dict(data)

    async def get_by_id(self, product_id: str) -> Product | None:
        """Получить товар по ID."""
        data = await self._repo.get_one({"_id": ObjectId(product_id)})
        if not data:
            return None
        return Product.from_dict(data)

    async def create(
        self,
        name: str,
        sku: str,
        barcode: str,
        category: str = "",
        location: str = "",
        price: float = 0.0,
        weight: float = 0.0,
        height: float = 0.0,
        width: float = 0.0,
        length: float = 0.0,
        qrcode: str | None = None,
        rfid: str | None = None,
    ) -> Product:
        """Создать товар."""
        now = datetime.utcnow()
        data = {
            "name": name,
            "sku": sku,
            "barcode": barcode,
            "qrcode": qrcode,
            "rfid": rfid,
            "category": category,
            "location": location,
            "quantity": 0,
            "price": price,
            "weight": weight,
            "height": height,
            "width": width,
            "length": length,
            "images": [],
            "created_at": now,
            "updated_at": now,
        }
        id = await self._repo.add(data)
        product = await self._repo.get_one({"_id": id})
        return Product.from_dict(product)

    async def update(self, product_id: str, **kwargs) -> Product | None:
        """Обновить товар."""
        kwargs["updated_at"] = datetime.utcnow()
        await self._repo.update({"_id": ObjectId(product_id)}, {"$set": kwargs})
        return await self.get_by_id(product_id)

    async def delete(self, product_id: str) -> bool:
        """Удалить товар и его изображения из хранилища."""
        product = await self.get_by_id(product_id)
        if product and self._storage:
            for img in product.images:
                try:
                    self._storage.delete_file(img["object_key"])
                except Exception:
                    pass
        return await self._repo.delete({"_id": ObjectId(product_id)})

    async def increase_quantity(self, product_id: str, quantity: int) -> Product | None:
        """Увеличить количество товара."""
        product = await self.get_by_id(product_id)
        if not product:
            return None
        new_qty = product.quantity + quantity
        return await self.update(product_id, quantity=new_qty)

    async def set_quantity(self, product_id: str, quantity: int) -> Product | None:
        """Установить количество товара."""
        return await self.update(product_id, quantity=quantity)

    async def search(self, query: str, limit: int = 20) -> list[Product]:
        """Поиск товаров."""
        results = await self._repo.get_many(
            {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"sku": {"$regex": query, "$options": "i"}},
                    {"barcode": {"$regex": query, "$options": "i"}},
                ]
            },
            limit=limit,
        )
        return [Product.from_dict(r) for r in results]

    async def get_all(
        self,
        limit: int = 100,
        skip: int = 0,
        search: str = "",
        category: str = "",
        min_price: float = 0,
        max_price: float = 0,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[Product], int]:
        """Получить все товары с фильтрацией, сортировкой и пагинацией."""
        query: dict = {}

        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"sku": {"$regex": search, "$options": "i"}},
                {"barcode": {"$regex": search, "$options": "i"}},
            ]

        if category:
            query["category"] = category

        price_filter: dict = {}
        if min_price > 0:
            price_filter["$gte"] = min_price
        if max_price > 0:
            price_filter["$lte"] = max_price
        if price_filter:
            query["price"] = price_filter

        sort_dir = 1 if sort_order == "asc" else -1
        sort_field = sort_by if sort_by in ("name", "price", "quantity", "created_at", "category") else "name"

        total = await self._repo.count(query)
        results = await self._repo.get_many(
            query,
            limit=limit,
            skip=skip,
            sort=[(sort_field, sort_dir)],
        )
        return [Product.from_dict(r) for r in results], total

    async def get_categories(self) -> list[str]:
        """Получить список категорий товаров."""
        results = await self._repo.get_many({}, limit=1000)
        categories = set()
        for r in results:
            cat = r.get("category", "")
            if cat:
                categories.add(cat)
        return sorted(categories)

    async def upload_image(self, product_id: str, file: "UploadFile") -> dict:
        """Загрузить изображение для товара."""
        if not self._storage or not self._image_validator:
            raise RuntimeError("Storage or image validator not configured")

        self._image_validator.validate_image_file(file)

        content = await file.read()
        raw_image = io.BytesIO(content)
        raw_img_size = len(content)
        filename = file.filename or "image.jpg"

        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
        image_id = str(uuid.uuid4())
        object_key = f"products/{product_id}/{image_id}.{ext}"

        self._storage.put_object(
            object_name=object_key,
            data=raw_image,
            size=raw_img_size,
            content_type=f"image/{ext}",
        )

        now = datetime.utcnow()
        image_entry = {
            "id": image_id,
            "filename": filename,
            "object_key": object_key,
            "uploaded_at": now.isoformat(),
        }

        await self._repo.update(
            {"_id": ObjectId(product_id)},
            {"$push": {"images": image_entry}, "$set": {"updated_at": now}},
        )

        return image_entry

    async def get_images(self, product_id: str) -> list[dict]:
        """Получить изображения товара с presigned URLs."""
        product = await self.get_by_id(product_id)
        if not product:
            return []
        if not self._storage:
            return product.images

        result = []
        for img in product.images:
            url = self._storage.generate_presigned_url(img["object_key"], expiration=3600)
            result.append({
                "id": img["id"],
                "filename": img["filename"],
                "url": url,
                "uploaded_at": img.get("uploaded_at", ""),
            })
        return result

    async def delete_image(self, product_id: str, image_id: str) -> bool:
        """Удалить изображение товара."""
        product = await self.get_by_id(product_id)
        if not product:
            return False

        img_to_delete = None
        for img in product.images:
            if img["id"] == image_id:
                img_to_delete = img
                break

        if not img_to_delete:
            return False

        if self._storage:
            try:
                self._storage.delete_file(img_to_delete["object_key"])
            except Exception:
                pass

        await self._repo.update(
            {"_id": ObjectId(product_id)},
            {
                "$pull": {"images": {"id": image_id}},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )
        return True
