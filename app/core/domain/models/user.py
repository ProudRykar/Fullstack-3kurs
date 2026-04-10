"""Модуль содержит доменную модель пользователя."""

from dataclasses import dataclass

from bson import ObjectId

from app.core.domain.models.role import Role


@dataclass
class User:
    """Доменная модель пользователя.

    Attributes:
        _id (ObjectId): Уникальный идентификатор пользователя
        username (str): Имя пользователя
        email (str): Email пользователя
        password_hash (str): Хэш пароля
        role (Role): Роль пользователя
    """

    _id: ObjectId
    username: str
    email: str
    password_hash: str
    role: Role = Role.USER

    @property
    def id(self) -> str:
        """Возвращает строковое представление ID.

        Returns:
            str: Уникальный идентификатор пользователя
        """
        return str(self._id)
