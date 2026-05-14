from unittest.mock import MagicMock

import pytest

from app.api.v1.utils import extract_client_ip
from app.core.exceptions import GeolocationProviderError


def _make_request(
    forwarded_for: str | None = None,
    real_ip: str | None = None,
    client_host: str | None = "1.2.3.4",
) -> MagicMock:
    """Build a minimal mock of fastapi.Request with configurable headers and client."""
    request = MagicMock()
    request.headers.get = lambda key, default=None: {
        "X-Forwarded-For": forwarded_for,
        "X-Real-IP": real_ip,
    }.get(key, default)
    request.client = MagicMock(host=client_host) if client_host is not None else None
    return request


def test_extract_client_ip_prefers_forwarded_for() -> None:
    request = _make_request(forwarded_for="8.8.8.8, 10.0.0.1", real_ip="1.1.1.1")
    assert extract_client_ip(request) == "8.8.8.8"


def test_extract_client_ip_uses_real_ip_when_no_forwarded_for() -> None:
    request = _make_request(real_ip="8.8.8.8")
    assert extract_client_ip(request) == "8.8.8.8"


def test_extract_client_ip_falls_back_to_client_host() -> None:
    request = _make_request(client_host="8.8.8.8")
    assert extract_client_ip(request) == "8.8.8.8"


def test_extract_client_ip_raises_when_client_is_none() -> None:
    request = _make_request(client_host=None)
    with pytest.raises(GeolocationProviderError, match="Unable to determine client IP address"):
        extract_client_ip(request)
