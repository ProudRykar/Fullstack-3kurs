import pytest
from unittest.mock import Mock, AsyncMock, patch

pytestmark = pytest.mark.asyncio

from app.adapters.gateways.redis import RedisGateway


# Тесты RedisGateway
async def test_connect_success():
    gateway = RedisGateway(db=0)

    mock_client = Mock()
    mock_client.ping = Mock(return_value=True)

    with patch("app.adapters.gateways.redis.redis.Redis", return_value=mock_client):
        await gateway.connect()

        mock_client.ping.assert_called_once()
        assert gateway._client == mock_client


async def test_connect_ping_false():
    gateway = RedisGateway(db=0)

    mock_client = Mock()
    mock_client.ping = Mock(return_value=False)

    with patch("app.adapters.gateways.redis.redis.Redis", return_value=mock_client):
        with pytest.raises(ConnectionError, match="Redis did not respond to PING"):
            await gateway.connect()

        mock_client.ping.assert_called_once()


async def test_connect_exception():
    gateway = RedisGateway(db=0)

    mock_client = Mock()
    mock_client.ping.side_effect = Exception("Redis error")

    with patch("app.adapters.gateways.redis.redis.Redis", return_value=mock_client):
        with pytest.raises(ConnectionError, match="Failed to connect to Redis"):
            await gateway.connect()


async def test_get_connection_calls_connect():
    gateway = RedisGateway(db=0)
    gateway.connect = AsyncMock()

    conn = await gateway.get_connection()

    gateway.connect.assert_awaited_once()
    assert conn == gateway._client


async def test_close():
    gateway = RedisGateway(db=0)
    mock_client = AsyncMock()
    mock_client.close = AsyncMock()
    gateway._client = mock_client

    await gateway.close()

    mock_client.close.assert_awaited_once()
    assert gateway._client is None
