"""Модуль содержит enum для ролей пользователей."""

from enum import StrEnum


class Role(StrEnum):
    """Роли пользователей в системе."""

    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"

    @classmethod
    def default(cls) -> "Role":
        """Возвращает роль по умолчанию для новых пользователей."""
        return cls.USER
