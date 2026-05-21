"""Модуль для построения и конфигурации контейнера зависимостей.

Контейнер позволяет централизованно управлять всеми сервисами, репозиториями
и шлюзами, используемыми в приложении, обеспечивая единый доступ к
одноэкземпляровым объектам и упрощая внедрение зависимостей.
"""

from typing import Any

from punq import Container, Scope

from app.adapters.gateways.mongo import MongoGateway
from app.adapters.gateways.redis import RedisGateway
from app.adapters.gateways.s3 import MinioGateway
from app.adapters.repositories.image_repo import ImageRepo
from app.adapters.repositories.mongo_repo import MongoRepo
from app.adapters.repositories.product_repo import ProductRepo
from app.adapters.repositories.receipt_repo import ReceiptRepo
from app.adapters.repositories.inventory_repo import InventoryRepo
from app.adapters.repositories.redis_blacklist_repo import RedisBlacklistRepo
from app.adapters.repositories.redis_rate_limit_repo import RedisRateLimitRepo
from app.adapters.repositories.user_repo import UserRepo
from app.adapters.repositories.warehouse_repo import WarehouseRepo, WarehouseCellRepo
from app.config import Config
from app.core.services.auth_service import AuthService
from app.core.services.security_service import SecurityService
from app.core.services.user_service import UserService
from app.core.services.product_service import ProductService
from app.core.services.receipt_service import ReceiptService
from app.core.services.inventory_service import InventoryService
from app.core.services.warehouse_service import WarehouseService
from app.core.services.validation_service import (
    ImageValidator,
    ValidationService,
)
from app.monitoring.api_monitor import ApiMonitor
from app.core.services.rbac_service import RBACService


def build_container() -> Container:
    """Создает и конфигурирует контейнер зависимостей.

    Регистрация включает:
        - Шлюзы (Mongo, Redis, Minio)
        - Репозитории (UserRepo, ImageRepo, Redis Blacklist/RateLimit)
        - Сервисы (AuthService, UserService, ValidationService, SecurityService)
        - Конфигурацию приложения (Config)
        - Монитор API (ApiMonitor)

    Используется паттерн singleton для одноэкземпляровых объектов, таких как
    шлюзы и сервисы.

    Returns:
        Container: Полностью настроенный контейнер зависимостей.
    """
    container = Container()

    def register_gateway_singleton(typ: type, factory: Any) -> None:
        """Регистрирует шлюз как одноэкземпляровый объект в контейнере.

        Args:
            typ (type): Класс шлюза
            factory (Any): Функция для создания экземпляра шлюза
        """
        container.register(typ, factory=factory, scope=Scope.singleton)

    register_gateway_singleton(MongoGateway, factory=lambda: MongoGateway())

    register_gateway_singleton(MinioGateway, factory=lambda: MinioGateway())

    def register_redis_pair(
        db_index: int, gateway_name_suffix: str, repo_cls: Any
    ) -> None:
        """Регистрация пары Redis: шлюз + репозиторий.

        Позволяет разделять БД Redis для разных целей (черный список токенов и
        rate limiting).

        Args:
            db_index (int): Индекс базы данных Redis
            gateway_name_suffix (str): Суффикс для создания уникального класса шлюза
            repo_cls (Any): Класс репозитория, который использует этот шлюз
        """
        gateway_type = type(
            f"RedisGatewayDb{db_index}_{gateway_name_suffix}", (RedisGateway,), {}
        )
        register_gateway_singleton(
            gateway_type, factory=lambda db=db_index: RedisGateway(db=db)
        )
        container.register(
            repo_cls,
            factory=lambda gw_type=gateway_type: repo_cls(
                gateway=container.resolve(gw_type)
            ),
        )

    register_redis_pair(0, "blacklist", RedisBlacklistRepo)
    register_redis_pair(1, "ratelimit", RedisRateLimitRepo)

    def register_mongo_repo(interface: Any, collection_name: str) -> None:
        """Регистрация Mongo репозитория с указанной коллекцией.

        Args:
            interface (Any): Интерфейс репозитория
            collection_name (str): Имя коллекции в MongoDB
        """
        container.register(
            interface,
            factory=lambda coll=collection_name: MongoRepo(
                gateway=container.resolve(MongoGateway),
                collection_name=coll,
            ),
        )

    register_mongo_repo(UserRepo, "users")
    register_mongo_repo(ImageRepo, "images")
    register_mongo_repo(ProductRepo, "products")
    register_mongo_repo(ReceiptRepo, "receipts")
    register_mongo_repo(InventoryRepo, "inventory")
    register_mongo_repo(WarehouseRepo, "warehouses")
    register_mongo_repo(WarehouseCellRepo, "warehouse_cells")

    container.register(SecurityService, SecurityService, scope=Scope.singleton)
    container.register(ValidationService, ValidationService, scope=Scope.singleton)
    container.register(ImageValidator, ImageValidator, scope=Scope.singleton)

    container.register(
        UserService,
        factory=lambda: UserService(
            user_repo=container.resolve(UserRepo),
            image_repo=container.resolve(ImageRepo),
            security=container.resolve(SecurityService),
            validator=container.resolve(ValidationService),
            image_validator=container.resolve(ImageValidator),
            storage=container.resolve(MinioGateway),
        ),
    )

    container.register(
        AuthService,
        factory=lambda: AuthService(
            repository=container.resolve(UserRepo),
            security=container.resolve(SecurityService),
            validation=container.resolve(ValidationService),
            redis_blacklist_repo=container.resolve(RedisBlacklistRepo),
            redis_rate_limit_repo=container.resolve(RedisRateLimitRepo),
            container=container,
        ),
    )

    container.register(Config, instance=Config())

    container.register(ApiMonitor, ApiMonitor, scope=Scope.singleton)

    container.register(
        ProductService,
        factory=lambda: ProductService(
            product_repo=container.resolve(ProductRepo),
            storage=container.resolve(MinioGateway),
            image_validator=container.resolve(ImageValidator),
        ),
    )

    container.register(
        ReceiptService,
        factory=lambda: ReceiptService(
            receipt_repo=container.resolve(ReceiptRepo),
            product_service=container.resolve(ProductService),
            warehouse_service=container.resolve(WarehouseService),
        ),
    )

    container.register(
        InventoryService,
        factory=lambda: InventoryService(
            inventory_repo=container.resolve(InventoryRepo),
            product_service=container.resolve(ProductService),
        ),
    )

    container.register(
        WarehouseService,
        factory=lambda: WarehouseService(
            warehouse_repo=container.resolve(WarehouseRepo),
            cell_repo=container.resolve(WarehouseCellRepo),
        ),
    )

    return container
