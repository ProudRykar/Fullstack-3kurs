"""Blank."""

from collections.abc import Callable

import paseto

from litestar.connection import Request
from litestar.datastructures import MutableScopeHeaders
from litestar.types import ASGIApp, Message, Receive, Scope, Send
from punq import Container

from app.api.schemas.user_dto import UserDTO
from app.config import config
from app.core.domain.models.role import Role
from app.core.services.user_service import UserService


def access_token_middleware(container: Container) -> Callable[[ASGIApp], ASGIApp]:
    """Фабрика ASGI middleware для проверки access_token и подстановки current_user.

    Args:
        container (Container): DI-контейнер с сервисами приложения.

    Returns:
        Callable[[ASGIApp], ASGIApp]: Функция, принимающая ASGI-приложение
        и возвращающая обёрнутое приложение с middleware.
    """

    def create_middleware(app: ASGIApp) -> ASGIApp:
        """Создаёт middleware для обработки access_token."""

        async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await app(scope, receive, send)
                return

            request = Request(scope, receive)
            user_service = container.resolve(UserService)
            current_user: UserDTO | None = None

            key = config.TOKEN_SECRET_KEY

            access_token = request.cookies.get("access_token")
            if access_token:
                try:
                    parsed = paseto.parse(
                        key=key,
                        purpose="local",
                        token=access_token,
                    )
                    claims = parsed["message"]

                    if claims.get("type") == "access":
                        user_id = claims["sub"]
                        user_data = await user_service.get_user_by_id(user_id)
                        if user_data:
                            current_user = UserDTO.fromrow(user_data)

                except Exception:
                    current_user = None

            scope["current_user"] = current_user

            async def send_wrapper(message: Message) -> None:
                """Wrapper для перехвата HTTP-ответа и добавления заголовков."""
                if message["type"] == "http.response.start":
                    headers = MutableScopeHeaders.from_message(message)
                    headers.add("access-control-allow-credentials", "true")

                    origin = request.headers.get("origin")

                    allowed = {"http://localhost:5173", "http://178.213.116.90:5173"}

                    if origin in allowed:
                        headers.add("access-control-allow-origin", origin)

                await send(message)

            await app(scope, receive, send_wrapper)

        return middleware

    return create_middleware