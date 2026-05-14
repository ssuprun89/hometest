from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.geolocation import GeolocationService, _is_local_ip
from tests.conftest import MOCK_GEO_RESPONSE


@pytest.mark.parametrize(
    "ip, expected",
    [
        ("127.0.0.1", True),
        ("localhost", True),
        ("LOCALHOST", True),
        ("0.0.0.0", True),
        ("192.168.1.1", True),
        ("10.0.0.1", True),
        ("172.16.0.1", True),
        ("8.8.8.8", False),
        ("1.1.1.1", False),
        ("not-an-ip", False),
    ],
)
def test_is_local_ip(ip: str, expected: bool) -> None:
    assert _is_local_ip(ip) == expected


async def test_get_by_ip_calls_get_geolocation() -> None:
    mock_client = MagicMock()
    mock_client.get_geolocation = AsyncMock(return_value=MOCK_GEO_RESPONSE)

    result = await GeolocationService(mock_client).get_by_ip("8.8.8.8")

    mock_client.get_geolocation.assert_called_once_with("8.8.8.8")
    assert result == MOCK_GEO_RESPONSE


async def test_get_by_client_ip_local_delegates_to_provider() -> None:
    """When the client IP is local, the provider should resolve the IP itself."""
    mock_client = MagicMock()
    mock_client.get_my_geolocation = AsyncMock(return_value=MOCK_GEO_RESPONSE)

    result = await GeolocationService(mock_client).get_by_client_ip("127.0.0.1")

    mock_client.get_my_geolocation.assert_called_once()
    mock_client.get_geolocation.assert_not_called()
    assert result == MOCK_GEO_RESPONSE


async def test_get_by_client_ip_public_passes_ip_explicitly() -> None:
    mock_client = MagicMock()
    mock_client.get_geolocation = AsyncMock(return_value=MOCK_GEO_RESPONSE)

    result = await GeolocationService(mock_client).get_by_client_ip("8.8.8.8")

    mock_client.get_geolocation.assert_called_once_with("8.8.8.8")
    mock_client.get_my_geolocation.assert_not_called()
    assert result == MOCK_GEO_RESPONSE
