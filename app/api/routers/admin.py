"""Модуль содержит эндпоинты для администрирования."""

from typing import Annotated

from bson import ObjectId
from litestar import Request, Router, get, patch
from litestar.di import Provide
from litestar.dto import DataclassDTO
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from litestar.params import Body
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from punq import Container

from app.api.exceptions.problem_factory import ErrorCode, ErrorMeta, problem_factory
from app.api.schemas.user_dto import RoleUpdateDTO, UserDTO
from app.core.domain.models.permission import Permission
from app.core.domain.models.role import Role
from app.core.errors.auth import ForbiddenError, UnauthorizedError
from app.core.middleware.rbac import require_permission
from app.core.services.auth_service import AuthService
from app.core.services.user_service import UserService


@get(
    "/users",
    summary="Список пользователей",
    description="Возвращает список всех пользователей (только для администраторов).",
    tags=["Admin"],
    status_code=HTTP_200_OK,
    dependencies={"current_admin": require_permission(Permission.USER_LIST)},
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Список пользователей",
            data_container=UserDTO,
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Пользователь не авторизован",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.AUTHENTICATION_ERROR,
                        detail="Пользователь не авторизован или сессия истекла",
                    ),
                )
            ],
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Доступ запрещён",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.AUTHORIZATION_ERROR,
                        detail="Доступ только для администраторов",
                    ),
                )
            ],
        ),
    },
)
async def list_users(
    container: Container,
    current_admin: UserDTO,
) -> list[UserDTO]:
    """Возвращает список всех пользователей."""
    user_service = container.resolve(UserService)

    users = await user_service.get_all_users()
    return [UserDTO.fromrow(user) for user in users]


@patch(
    "/users/{user_id:str}/role",
    summary="Изменение роли пользователя",
    description="Изменяет роль пользователя (только для администраторов).",
    tags=["Admin"],
    status_code=HTTP_200_OK,
    dependencies={"current_admin": require_permission(Permission.USER_UPDATE_ROLE)},
    dto=DataclassDTO[RoleUpdateDTO],
    return_dto=DataclassDTO[UserDTO],
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Роль успешно обновлена",
            data_container=UserDTO,
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Пользователь не авторизован",
            data_container=ErrorMeta,
        ),
        HTTP_403_FORBIDDEN: ResponseSpec(
            description="Доступ запрещён",
            data_container=ErrorMeta,
        ),
        HTTP_404_NOT_FOUND: ResponseSpec(
            description="Пользователь не найден",
            data_container=ErrorMeta,
        ),
        HTTP_422_UNPROCESSABLE_ENTITY: ResponseSpec(
            description="Невалидная роль",
            data_container=ErrorMeta,
        ),
    },
)
async def update_user_role(
    container: Container,
    current_admin: UserDTO,
    user_id: str,
    data: RoleUpdateDTO,
) -> UserDTO:
    """Изменяет роль пользователя."""
    user_service = container.resolve(UserService)

    if data.role not in [Role.USER.value, Role.ADMIN.value]:
        raise ValueError(f"Невалидная роль: {data.role}")

    user = await user_service.update_user_role(user_id, data.role)
    if not user:
        raise ValueError("Пользователь не найден")

    return UserDTO.fromrow(user)


admin_router = Router(
    path="/admin",
    tags=["Admin"],
    route_handlers=[list_users, update_user_role],
)