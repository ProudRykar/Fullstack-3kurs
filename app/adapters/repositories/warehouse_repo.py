"""Репозиторий для складов."""

from app.adapters.interfaces.db import DBGatewayInterface
from app.adapters.repositories.mongo_repo import MongoRepo


class WarehouseRepo(MongoRepo):
    """Репозиторий складов."""

    def __init__(self, gateway: DBGatewayInterface) -> None:
        super().__init__(gateway, collection_name="warehouses")


class WarehouseCellRepo(MongoRepo):
    """Репозиторий ячеек склада."""

    def __init__(self, gateway: DBGatewayInterface) -> None:
        super().__init__(gateway, collection_name="warehouse_cells")
