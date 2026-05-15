"""Модуль содержит RBAC guard для проверки прав доступа."""

import paseto
from litestar import Request
from litestar.di import Provide
from punq import Container

from app.api.schemas.user_dto import UserDTO
from app.config import token_key
from app.core.domain.models.permission import Permission
from app.core.domain.models.role import Role
from app.core.errors.auth import ForbiddenError, UnauthorizedError
from app.core.errors.security import InvalidTokenError
from app.core.services.rbac_service import RBACService
from app.core.services.user_service import UserService


async def get_current_user(
    request: Request, container: Container
) -> UserDTO:
    """Извлекает и возвращает текущего пользователя из access_token cookie.

    Raises:
        UnauthorizedError: Если токен отсутствует или невалиден.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise UnauthorizedError("Пользователь не авторизован или сессия истекла")

    try:
        parsed = paseto.parse(key=token_key, purpose="local", token=token)
        claims = parsed["message"]

        if claims.get("type") != "access":
            raise UnauthorizedError("Неверный тип токена")

        user_id = claims.get("sub")
        if not user_id:
            raise UnauthorizedError("В токене отсутствует идентификатор пользователя")

    except Exception:
        raise InvalidTokenError("Невалидный токен") from None

    user_service = container.resolve(UserService)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise UnauthorizedError("Пользователь не найден в базе данных")

    return UserDTO.fromrow(user)


def require_permission(permission: Permission) -> Provide:
    """Создаёт dependency для проверки конкретного разрешения.

    Использование:
        @get(dependencies={"user": require_permission(Permission.PRODUCT_VIEW)})
        async def my_endpoint(user: UserDTO) -> ...:
            ...
    """
    async def _check(request: Request, container: Container) -> UserDTO:
        user = await get_current_user(request, container)
        if not RBACService.has_permission(user.role, permission):
            raise ForbiddenError(
                f"Недостаточно прав. Требуется разрешение: {permission.value}"
            )
        return user
    return Provide(_check)


def require_any_permission(permissions: list[Permission]) -> Provide:
    """Создаёт dependency для проверки хотя бы одного разрешения."""
    async def _check(request: Request, container: Container) -> UserDTO:
        user = await get_current_user(request, container)
        if not RBACService.has_any_permission(user.role, permissions):
            raise ForbiddenError(
                f"Недостаточно прав. Требуется одно из: {[p.value for p in permissions]}"
            )
        return user
    return Provide(_check)


def require_role(allowed_roles: list[Role]) -> Provide:
    """Создаёт dependency для проверки роли пользователя."""
    async def _check(request: Request, container: Container) -> UserDTO:
        user = await get_current_user(request, container)
        user_role = Role(user.role)
        if user_role not in allowed_roles:
            raise ForbiddenError(
                f"Доступ запрещён. Требуется одна из ролей: {[r.value for r in allowed_roles]}"
            )
        return user
    return Provide(_check)