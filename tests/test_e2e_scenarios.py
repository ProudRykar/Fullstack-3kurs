"""
Сквозные (E2E) тесты основных бизнес-сценариев.

Тестируют полные бизнес-потоки через сервисный слой
с замокированными gateway (MongoDB, Redis, MinIO, paseto).
"""

import sys
import paseto
from unittest.mock import AsyncMock, Mock, MagicMock, PropertyMock
from bson import ObjectId
import pytest

from app.core.services.auth_service import AuthService
from app.core.services.product_service import ProductService
from app.core.services.receipt_service import ReceiptService
from app.core.services.inventory_service import InventoryService
from app.core.services.warehouse_service import WarehouseService
from app.core.services.user_service import UserService
from app.core.services.rbac_service import RBACService
from app.core.domain.models.permission import Permission
from app.core.domain.models.role import Role
from app.core.domain.models.product import Product
from app.adapters.repositories.abc_repo import RepositoryInterface


def make_mock_repo(**extra_methods):
    base = {
        "get_one": AsyncMock(),
        "get_many": AsyncMock(return_value=[]),
        "get_all": AsyncMock(return_value=[]),
        "add": AsyncMock(return_value=ObjectId()),
        "update": AsyncMock(),
        "delete": AsyncMock(),
        "count": AsyncMock(return_value=0),
    }
    base.update(extra_methods)
    return MagicMock(**base)


def make_counting_repo(**extra_methods):
    coll_mock = MagicMock()
    coll_mock.count_documents = AsyncMock(return_value=0)
    repo = make_mock_repo(
        _init_collection=AsyncMock(return_value=coll_mock),
        **extra_methods,
    )
    return repo


# ──────────────────────────────────────────────
# 2. E2E: Аутентификация
# ──────────────────────────────────────────────

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_auth_register_and_login():
    user_id = ObjectId()
    repo = make_mock_repo(
        get_one=AsyncMock(side_effect=[
            None, None,
            {
                "_id": user_id,
                "username": "e2euser",
                "email": "e2e@test.com",
                "password_hash": "ser:hash",
            },
        ]),
        count=AsyncMock(return_value=0),
    )
    security = MagicMock()
    security.hash_password = Mock(return_value=("salt", "hash"))
    security.serialize_hash = Mock(return_value="ser:hash")
    security.deserialize_hash = Mock(return_value=("salt", "hash"))
    security.verify_hash = Mock(return_value=True)

    validator = MagicMock()
    validator.validate_password = Mock()
    validator.validate_username = Mock()
    validator.validate_email = Mock()
    validator.validate_credentials = Mock()

    image_validator = MagicMock()
    image_validator.validate_image_file = Mock(return_value=True)

    storage = MagicMock()
    image_repo = make_mock_repo()

    user_svc = UserService(
        user_repo=repo,
        image_repo=image_repo,
        security=security,
        validator=validator,
        image_validator=image_validator,
        storage=storage,
    )

    created = await user_svc.create_user("e2euser", "E2E@TEST.COM", "ValidPass1!", "ValidPass1!")
    assert created.username == "e2euser"
    assert created.email == "e2e@test.com"

    repo.get_one = AsyncMock(return_value={
        "_id": user_id,
        "username": "e2euser",
        "email": "e2e@test.com",
        "password_hash": "ser:hash",
    })

    container = MagicMock()
    fake_user_service = AsyncMock()
    fake_user_service.get_user_by_id = AsyncMock(return_value={"_id": str(user_id), "username": "e2euser"})
    container.resolve = Mock(return_value=fake_user_service)

    paseto.create = MagicMock(side_effect=["ACCESS_TOKEN", "REFRESH_TOKEN"])
    paseto.parse = MagicMock(return_value={"message": {"type": "access", "sub": str(user_id), "jti": "ajti"}})

    auth_svc = AuthService(
        container=container,
        repository=repo,
        security=security,
        validation=validator,
        redis_blacklist_repo=MagicMock(
            is_blacklisted=AsyncMock(return_value=False),
            add_to_blacklist=AsyncMock(),
        ),
        redis_rate_limit_repo=MagicMock(),
    )

    user_dto, access_token, refresh_token = await auth_svc.auth_existing_user("e2euser", "ValidPass1!", client_ip="127.0.0.1")
    assert user_dto.username == "e2euser"


# ──────────────────────────────────────────────
# 3. E2E: CRUD товара
# ──────────────────────────────────────────────

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_product_crud():
    product_id = ObjectId()
    product_repo = make_mock_repo(
        add=AsyncMock(return_value=product_id),
    )
    product_repo.get_one = AsyncMock(return_value=Product(
        _id=product_id, name="E2E Product", sku="E2E-001", barcode="2000000000999",
        price=199.99, quantity=10, category="test",
    ).to_dict())

    service = ProductService(product_repo=product_repo)

    created = await service.create(
        name="E2E Product",
        sku="E2E-001",
        barcode="2000000000999",
        price=199.99,
        category="test",
    )
    assert created.name == "E2E Product"


# ──────────────────────────────────────────────
# 4. E2E: Приёмка
# ──────────────────────────────────────────────

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_receipt_flow():
    wh_repo = make_mock_repo()
    cell_repo = make_mock_repo(
        get_many=AsyncMock(return_value=[{"_id": ObjectId(), "code": "A1", "cell_quantity": 0, "cell_capacity": 100}]),
    )
    wh_svc = WarehouseService(warehouse_repo=wh_repo, cell_repo=cell_repo)

    product_repo = make_mock_repo(get_one=AsyncMock(return_value={
        "_id": ObjectId(), "name": "Prod", "barcode": "2000000000888", "price": 50.0, "quantity": 10,
    }))
    product_svc = ProductService(product_repo=product_repo)

    receipt_repo = make_counting_repo(
        get_one=AsyncMock(return_value={
            "_id": ObjectId(), "number": "ПР-00001", "status": "draft", "items": [], "total": 0,
            "date": None, "created_by": "user1", "confirmed_at": None, "warehouse_id": "wh-1",
        }),
        get_many=AsyncMock(return_value=[{"_id": ObjectId(), "number": "ПР-00001", "status": "draft"}]),
        add=AsyncMock(return_value=ObjectId()),
    )
    receipt_svc = ReceiptService(
        receipt_repo=receipt_repo,
        product_service=product_svc,
        warehouse_service=wh_svc,
    )

    receipt = await receipt_svc.create(created_by="user1", warehouse_id="wh-1")
    assert receipt is not None


# ──────────────────────────────────────────────
# 5. E2E: Инвентаризация
# ──────────────────────────────────────────────

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_inventory_flow():
    product_repo = make_mock_repo(get_one=AsyncMock(return_value={
        "_id": ObjectId(), "name": "Prod", "barcode": "2000000000777", "quantity": 10,
    }))
    product_svc = ProductService(product_repo=product_repo)

    inv_repo = make_counting_repo(
        get_one=AsyncMock(return_value={
            "_id": ObjectId(), "number": "ИНВ-00001", "status": "draft", "scans": [],
            "created_by": "user1", "warehouse_id": "wh-1",
        }),
        get_many=AsyncMock(return_value=[{"_id": ObjectId(), "number": "ИНВ-00001", "status": "active"}]),
        add=AsyncMock(return_value=ObjectId()),
    )
    inv_svc = InventoryService(inventory_repo=inv_repo, product_service=product_svc)

    inv = await inv_svc.create(created_by="user1", warehouse_id="wh-1")
    assert inv is not None

    product_repo.get_one = AsyncMock(return_value={
        "_id": ObjectId(), "name": "Prod", "barcode": "2000000000777", "quantity": 10,
    })
    inv_id_str = str(ObjectId())
    product_repo.get_one = AsyncMock(return_value={
        "_id": ObjectId(), "name": "Prod", "barcode": "2000000000777", "quantity": 10,
    })
    await inv_svc.scan(inventory_id=inv_id_str, barcode="2000000000777", scanned_quantity=5)

    inv_repo.get_one = AsyncMock(return_value={
        "_id": ObjectId(), "number": "ИНВ-00001", "status": "active",
        "scans": [{"barcode": "2000000000777", "scanned_quantity": 5}],
    })
    await inv_svc.complete(inventory_id=inv_id_str)


# ──────────────────────────────────────────────
# 6. E2E: RBAC
# ──────────────────────────────────────────────

class TestE2ERBAC:
    @pytest.mark.e2e
    def test_admin_has_privileged_permissions(self):
        for perm in Permission:
            if perm in (Permission.USER_REGISTER,):
                continue
            assert RBACService.has_permission(Role.ADMIN, perm), f"Admin should have {perm}"

    @pytest.mark.e2e
    def test_guest_only_register_and_login(self):
        for perm in Permission:
            expected = perm in (Permission.USER_REGISTER, Permission.USER_LOGIN)
            assert RBACService.has_permission(Role.GUEST, perm) == expected, \
                f"Guest {perm}={expected}"

    @pytest.mark.e2e
    def test_user_permissions(self):
        assert RBACService.has_permission(Role.USER, Permission.PRODUCT_VIEW)
        assert RBACService.has_permission(Role.USER, Permission.WAREHOUSE_VIEW)
        assert not RBACService.has_permission(Role.USER, Permission.USER_LIST)
        assert not RBACService.has_permission(Role.USER, Permission.USER_UPDATE_ROLE)


# ──────────────────────────────────────────────
# 7. E2E: Валидация
# ──────────────────────────────────────────────

@pytest.mark.e2e
def test_e2e_validation_rules():
    from app.core.services.validation_service import ValidationService, ImageValidator
    from app.config import config as app_config

    validator = ValidationService(config_instance=app_config)

    validator.validate_username("e2e-user")
    validator.validate_email("e2e@test.com")
    validator.validate_credentials("  validuser  ", "ValidPass1!", is_email=False)

    image_validator = ImageValidator(config=app_config)
    image_validator._validate_extension("test.jpg")
    image_validator._validate_filename(MagicMock(filename="test.jpg"))
