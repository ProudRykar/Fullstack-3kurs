"""Модуль содержит RBAC guard для проверки прав доступа."""

from litestar import Request
from litestar.di import Provide
from punq import Container

from app.api.schemas.user_dto import UserDTO
from app.config import token_key
from app.core.domain.models.permission import (
    ROLE_PERMISSIONS,
    Permission,
)
from app.core.domain.models.role import Role
from app.core.errors.auth import ForbiddenError
from app.core.errors.security import InvalidTokenError
import paseto


async def require_permission(
    request: Request, container: Container, permission: Permission
) -> None:
    """Dependency для проверки разрешения.

    Raises:
        ForbiddenError: Если нет разрешения.
    """
    user = await get_user_from_request(request, container)
    if user is None:
        return

    role = user.role
    role_perms = ROLE_PERMISSIONS.get(role, [])
    if permission not in role_perms:
        raise ForbiddenError(
            f"Недостаточно прав для выполнения операции. Требуется: {permission.value}"
        )


async def require_any_permission(
    request: Request, container: Container, permissions: list[Permission]
) -> None:
    """Dependency для проверки хотя бы одного разрешения.

    Raises:
        ForbiddenError: Если нет ни одного разрешения.
    """
    user = await get_user_from_request(request, container)
    if user is None:
        return

    role = user.role
    role_perms = ROLE_PERMISSIONS.get(role, [])
    if not any(p in role_perms for p in permissions):
        raise ForbiddenError(
            f"Недостаточно прав для выполнения операции. Требуется одно из: {[p.value for p in permissions]}"
        )


async def require_role(
    request: Request, container: Container, allowed_roles: list[Role]
) -> None:
    """Dependency для проверки роли.

    Raises:
        ForbiddenError: Если роль не соответствует.
    """
    user = await get_user_from_request(request, container)
    if user is None:
        raise ForbiddenError("Доступ только для авторизованных пользователей")

    user_role = Role(user.role)
    if user_role not in allowed_roles:
        raise ForbiddenError(
            f"Доступ запрещён. Требуется одна из ролей: {[r.value for r in allowed_roles]}"
        )


async def get_user_from_request(
    request: Request, container: Container
) -> UserDTO | None:
    """Извлекает пользователя из токена в запросе.

    Returns:
        UserDTO | None: Пользователь или None, если не авторизован.
    """
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        parsed = paseto.parse(key=token_key, purpose="local", token=token)
        claims = parsed["message"]

        if claims.get("type") != "access":
            return None

        role = claims.get("role", Role.USER.value)

        return UserDTO(
            id=claims.get("sub", ""),
            username=claims.get("username", ""),
            email=claims.get("email", ""),
            role=role,
        )
    except Exception:
        return None


def require_permission_dep(permission: Permission):
    """Создаёт dependency для проверки разрешения.

    Args:
        permission (Permission): Требуемое разрешение.

    Returns:
        Provide dependency для Litestar.
    """
    return Provide(lambda _: require_permission(permission=permission))


def require_role_dep(allowed_roles: list[Role]):
    """Создаёт dependency для проверки роли.

    Args:
        allowed_roles (list[Role]): Список допустимых ролей.

    Returns:
        Provide dependency для Litestar.
    """
    return Provide(lambda _: require_role(allowed_roles=allowed_roles))
