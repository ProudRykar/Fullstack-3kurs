"""Объединение всех роутеров API."""

from litestar import Router

from .admin import admin_router
from .auth import auth_router
from .health import health_router
from .inventory import inventory_router
from .products import products_router
from .receipts import receipts_router
from .user import users_router
from .warehouses import warehouses_router


api_routers = Router(
    path="",
    route_handlers=[
        health_router,
        auth_router,
        users_router,
        products_router,
        receipts_router,
        inventory_router,
        warehouses_router,
        admin_router,
    ],
)
