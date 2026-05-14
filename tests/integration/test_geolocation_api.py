import httpx
import respx
from httpx import AsyncClient

from app.core.config import settings
from tests.conftest import MOCK_IP, MOCK_IP_API_RESPONSE

BASE_URL = f"{settings.ip_api_base_url}/json"


async def test_get_geolocation_by_ip_success(api_client: AsyncClient) -> None:
    with respx.mock:
        respx.get(f"{BASE_URL}/{MOCK_IP}").mock(
            return_value=httpx.Response(200, json=MOCK_IP_API_RESPONSE)
        )
        response = await api_client.get(f"/api/v1/geolocation/{MOCK_IP}")

    assert response.status_code == 200
    data = response.json()
    assert data["ip"] == MOCK_IP
    assert data["country"] == "United States"
    assert data["city"] == "Ashburn"
    assert data["country_code"] == "US"
    assert data["timezone"] == "America/New_York"


async def test_get_geolocation_by_ip_not_found(api_client: AsyncClient) -> None:
    with respx.mock:
        respx.get(f"{BASE_URL}/{MOCK_IP}").mock(
            return_value=httpx.Response(
                200, json={"status": "fail", "message": "not found", "query": MOCK_IP}
            )
        )
        response = await api_client.get(f"/api/v1/geolocation/{MOCK_IP}")

    assert response.status_code == 404
    assert response.json()["error"] == "Geolocation not found"


async def test_get_geolocation_by_ip_invalid_format(api_client: AsyncClient) -> None:
    """FastAPI rejects malformed IPs before they reach the service."""
    response = await api_client.get("/api/v1/geolocation/not-an-ip")

    assert response.status_code == 422


async def test_get_geolocation_by_ip_provider_timeout(api_client: AsyncClient) -> None:
    with respx.mock:
        respx.get(f"{BASE_URL}/{MOCK_IP}").mock(side_effect=httpx.TimeoutException("timed out"))
        response = await api_client.get(f"/api/v1/geolocation/{MOCK_IP}")

    assert response.status_code == 503
    assert response.json()["error"] == "Geolocation provider unavailable"


async def test_get_geolocation_by_ip_provider_http_error(api_client: AsyncClient) -> None:
    with respx.mock:
        respx.get(f"{BASE_URL}/{MOCK_IP}").mock(return_value=httpx.Response(429))
        response = await api_client.get(f"/api/v1/geolocation/{MOCK_IP}")

    assert response.status_code == 503


async def test_get_my_geolocation_with_forwarded_header(api_client: AsyncClient) -> None:
    """X-Forwarded-For should be used as the client IP when present."""
    with respx.mock:
        respx.get(f"{BASE_URL}/{MOCK_IP}").mock(
            return_value=httpx.Response(200, json=MOCK_IP_API_RESPONSE)
        )
        response = await api_client.get(
            "/api/v1/geolocation/me",
            headers={"X-Forwarded-For": f"{MOCK_IP}, 10.0.0.1"},
        )

    assert response.status_code == 200
    assert response.json()["ip"] == MOCK_IP


async def test_get_my_geolocation_local_ip_delegates_to_provider(api_client: AsyncClient) -> None:
    """When the detected IP is local, the provider resolves the IP on its own."""
    with respx.mock:
        # No X-Forwarded-For — test client connects from 127.0.0.1 which is local
        respx.get(f"{BASE_URL}/").mock(return_value=httpx.Response(200, json=MOCK_IP_API_RESPONSE))
        response = await api_client.get("/api/v1/geolocation/me")

    assert response.status_code == 200
    assert response.json()["ip"] == MOCK_IP


async def test_get_my_geolocation_with_real_ip_header(api_client: AsyncClient) -> None:
    """X-Real-IP should be used as the client IP when X-Forwarded-For is absent."""
    with respx.mock:
        respx.get(f"{BASE_URL}/{MOCK_IP}").mock(
            return_value=httpx.Response(200, json=MOCK_IP_API_RESPONSE)
        )
        response = await api_client.get(
            "/api/v1/geolocation/me",
            headers={"X-Real-IP": MOCK_IP},
        )

    assert response.status_code == 200
    assert response.json()["ip"] == MOCK_IP


async def test_get_geolocation_provider_connection_error(api_client: AsyncClient) -> None:
    """A network-level connection error should return HTTP 503."""
    with respx.mock:
        respx.get(f"{BASE_URL}/{MOCK_IP}").mock(
            side_effect=httpx.ConnectError("connection refused")
        )
        response = await api_client.get(f"/api/v1/geolocation/{MOCK_IP}")

    assert response.status_code == 503
    assert "geolocation provider" in response.json()["error"].lower()


async def test_get_geolocation_private_ip_rejected_by_provider(api_client: AsyncClient) -> None:
    """A valid-format private IP that ip-api.com rejects should return HTTP 422."""
    private_ip = "192.168.1.1"
    with respx.mock:
        respx.get(f"{BASE_URL}/{private_ip}").mock(
            return_value=httpx.Response(
                200, json={"status": "fail", "message": "private range", "query": private_ip}
            )
        )
        response = await api_client.get(f"/api/v1/geolocation/{private_ip}")

    assert response.status_code == 422
    assert response.json()["error"] == "Invalid IP address"
