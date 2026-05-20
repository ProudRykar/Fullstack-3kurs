"""Blank."""

from collections.abc import Callable
from datetime import datetime, timezone

import paseto

from litestar.connection import Request
from litestar.datastructures import MutableScopeHeaders
from litestar.types import ASGIApp, Message, Receive, Scope, Send
from punq import Container

from app.api.schemas.user_dto import UserDTO
from app.config import config
from app.core.domain.models.role import Role
from app.core.services.auth_service import AuthService
from app.core.services.user_service import UserService


def access_token_middleware(container: Container) -> Callable[[ASGIApp], ASGIApp]:
    """Фабрика ASGI middleware для проверки access_token и подстановки current_user."""

    def create_middleware(app: ASGIApp) -> ASGIApp:
        """Создаёт middleware для обработки access_token."""

        async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await app(scope, receive, send)
                return
            
            # Исключаем эндпоинт обновления из middleware
            path = scope.get("path", "")
            if path in ["/auth/refresh", "/auth/login", "/auth/logout"]:
                await app(scope, receive, send)
                return
            
            request = Request(scope, receive)
            
            # Получаем сервисы из контейнера
            auth_service = container.resolve(AuthService)
            user_service = container.resolve(UserService)
            
            access_token = request.cookies.get("access_token")
            refresh_token = request.cookies.get("refresh_token")
            
            should_refresh = False
            new_access_token = None
            current_user = None
            
            if access_token:
                try:
                    parsed = paseto.parse(
                        key=config.TOKEN_SECRET_KEY,
                        purpose="local",
                        token=access_token,
                    )
                    claims = parsed["message"]
                    
                    # Проверяем тип токена
                    if claims.get("type") == "access":
                        exp = claims.get("exp", 0)
                        current_time = datetime.now(timezone.utc).timestamp()
                        
                        # Обновляем только если осталось менее 5 минут
                        if exp - current_time < 300:  # 5 minutes
                            should_refresh = True
                        else:
                            # Токен еще валидный, получаем пользователя
                            user_id = claims.get("sub")
                            if user_id:
                                user_data = await user_service.get_user_by_id(user_id)
                                if user_data:
                                    current_user = UserDTO.fromrow(user_data)
                except Exception as e:
                    # Токен недействителен, нужно обновить
                    should_refresh = True
            
            # Обновляем токен если нужно
            if should_refresh and refresh_token:
                try:
                    result = await auth_service.refresh_access_token(refresh_token)
                    new_access_token = result.get("access_token")
                    
                    # Получаем пользователя из нового токена
                    if new_access_token:
                        parsed = paseto.parse(
                            key=config.TOKEN_SECRET_KEY,
                            purpose="local",
                            token=new_access_token,
                        )
                        claims = parsed["message"]
                        user_id = claims.get("sub")
                        if user_id:
                            user_data = await user_service.get_user_by_id(user_id)
                            if user_data:
                                current_user = UserDTO.fromrow(user_data)
                except Exception as e:
                    # Не удалось обновить токен
                    pass
            
            # Сохраняем пользователя в scope
            scope["current_user"] = current_user
            if new_access_token:
                scope["new_access_token"] = new_access_token
            
            async def send_wrapper(message: Message):
                if message["type"] == "http.response.start":
                    headers = MutableScopeHeaders.from_message(message)
                    
                    # Добавляем новый access token если есть
                    if new_access_token:
                        headers.add(
                            "Set-Cookie",
                            f"access_token={new_access_token}; HttpOnly; Path=/; Max-Age={config.ACCESS_TOKEN_EXPIRE_SECONDS}; SameSite=Lax"
                        )
                    
                    # Добавляем CORS заголовки
                    origin = request.headers.get("origin", "")
                    allowed_origins = {"http://localhost:5173", "http://178.213.116.90:5173"}
                    
                    if origin in allowed_origins:
                        headers.add("Access-Control-Allow-Origin", origin)
                        headers.add("Access-Control-Allow-Credentials", "true")
                
                await send(message)
            
            await app(scope, receive, send_wrapper)
        
        return middleware
    
    return create_middleware