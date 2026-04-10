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
    USER_LIST = "user:list"
    USER_UPDATE_ROLE = "user:update_role"
    IMAGE_LIST_ALL = "image:list_all"


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
    ],
    "admin": [
        Permission.USER_LOGIN,
        Permission.USER_VIEW_OWN,
        Permission.IMAGE_UPLOAD,
        Permission.IMAGE_LIST_OWN,
        Permission.IMAGE_DELETE_OWN,
        Permission.USER_LIST,
        Permission.USER_UPDATE_ROLE,
        Permission.IMAGE_LIST_ALL,
    ],
}
