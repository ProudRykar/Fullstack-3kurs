"""Модуль содержит enum для разрешений (permissions)."""

from enum import StrEnum


class Permission(StrEnum):
    """Разрешения в системе."""

    USER_REGISTER = "user:register"
    USER_LOGIN = "user:login"
    USER_VIEW_OWN = "user:view_own"
    IMAGE_UPLOAD = "image:upload"
    IMAGE_LIST_OWN = "image:list_own"
    IMAGE_DELETE_OWN = "image:delete_own"
    IMAGE_LIST_ALL = "image:list_all"
    PRODUCT_VIEW = "product:view"
    PRODUCT_CREATE = "product:create"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"
    RECEIPT_CREATE = "receipt:create"
    RECEIPT_VIEW = "receipt:view"
    RECEIPT_ADD_ITEM = "receipt:add_item"
    RECEIPT_CONFIRM = "receipt:confirm"
    RECEIPT_CANCEL = "receipt:cancel"
    INVENTORY_CREATE = "inventory:create"
    INVENTORY_VIEW = "inventory:view"
    INVENTORY_SCAN = "inventory:scan"
    INVENTORY_COMPLETE = "inventory:complete"
    WAREHOUSE_VIEW = "warehouse:view"
    WAREHOUSE_CREATE = "warehouse:create"
    WAREHOUSE_UPDATE = "warehouse:update"
    WAREHOUSE_DELETE = "warehouse:delete"
    WAREHOUSE_CELL_CREATE = "warehouse:cell:create"
    WAREHOUSE_CELL_DELETE = "warehouse:cell:delete"
    WAREHOUSE_CELL_PLACE = "warehouse:cell:place"
    USER_LIST = "user:list"
    USER_UPDATE_ROLE = "user:update_role"


ROLE_PERMISSIONS = {
    "guest": [
        Permission.USER_REGISTER,
        Permission.USER_LOGIN,
    ],
    "user": [
        Permission.USER_LOGIN,
        Permission.USER_VIEW_OWN,
        Permission.IMAGE_UPLOAD,
        Permission.IMAGE_LIST_OWN,
        Permission.IMAGE_DELETE_OWN,
        Permission.PRODUCT_VIEW,
        Permission.RECEIPT_CREATE,
        Permission.RECEIPT_VIEW,
        Permission.RECEIPT_ADD_ITEM,
        Permission.INVENTORY_CREATE,
        Permission.INVENTORY_VIEW,
        Permission.INVENTORY_SCAN,
        Permission.WAREHOUSE_VIEW,
        Permission.WAREHOUSE_CREATE,
        Permission.WAREHOUSE_UPDATE,
        Permission.WAREHOUSE_CELL_CREATE,
        Permission.WAREHOUSE_CELL_DELETE,
        Permission.WAREHOUSE_CELL_PLACE,
    ],
    "admin": [
        Permission.USER_LOGIN,
        Permission.USER_VIEW_OWN,
        Permission.IMAGE_UPLOAD,
        Permission.IMAGE_LIST_OWN,
        Permission.IMAGE_DELETE_OWN,
        Permission.IMAGE_LIST_ALL,
        Permission.PRODUCT_VIEW,
        Permission.PRODUCT_CREATE,
        Permission.PRODUCT_UPDATE,
        Permission.PRODUCT_DELETE,
        Permission.RECEIPT_CREATE,
        Permission.RECEIPT_VIEW,
        Permission.RECEIPT_ADD_ITEM,
        Permission.RECEIPT_CONFIRM,
        Permission.RECEIPT_CANCEL,
        Permission.INVENTORY_CREATE,
        Permission.INVENTORY_VIEW,
        Permission.INVENTORY_SCAN,
        Permission.INVENTORY_COMPLETE,
        Permission.WAREHOUSE_VIEW,
        Permission.WAREHOUSE_CREATE,
        Permission.WAREHOUSE_UPDATE,
        Permission.WAREHOUSE_DELETE,
        Permission.WAREHOUSE_CELL_CREATE,
        Permission.WAREHOUSE_CELL_DELETE,
        Permission.WAREHOUSE_CELL_PLACE,
        Permission.USER_LIST,
        Permission.USER_UPDATE_ROLE,
    ],
}
