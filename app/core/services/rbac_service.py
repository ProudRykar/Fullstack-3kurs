"""Модуль содержит RBAC service для проверки прав доступа."""

from app.core.domain.models.permission import (
    ROLE_PERMISSIONS,
    Permission,
)
from app.core.domain.models.role import Role


class RBACService:
    """Сервис для проверки прав доступа (RBAC)."""

    @staticmethod
    def has_permission(role: str, permission: Permission) -> bool:
        """Проверяет, есть ли у роли указанное разрешение.

        Args:
            role (str): Роль пользователя.
            permission (Permission): Разрешение для проверки.

        Returns:
            bool: True, если разрешение есть у роли.
        """
        role_perms = ROLE_PERMISSIONS.get(role, [])
        return permission in role_perms

    @staticmethod
    def has_any_permission(role: str, permissions: list[Permission]) -> bool:
        """Проверяет, есть ли у роли хотя бы одно из разрешений.

        Args:
            role (str): Роль пользователя.
            permissions (list[Permission]): Список разрешений для проверки.

        Returns:
            bool: True, если есть хотя бы одно разрешение.
        """
        role_perms = ROLE_PERMISSIONS.get(role, [])
        return any(p in role_perms for p in permissions)

    @staticmethod
    def get_role_permissions(role: str) -> list[Permission]:
        """Возвращает список разрешений для роли.

        Args:
            role (str): Роль пользователя.

        Returns:
            list[Permission]: Список разрешений роли.
        """
        return ROLE_PERMISSIONS.get(role, [])
