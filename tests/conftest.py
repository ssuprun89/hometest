import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app
from app.models.geolocation import GeolocationResponse

MOCK_IP = "8.8.8.8"

MOCK_IP_API_RESPONSE = {
    "status": "success",
    "country": "United States",
    "countryCode": "US",
    "region": "VA",
    "regionName": "Virginia",
    "city": "Ashburn",
    "zip": "20149",
    "lat": 39.03,
    "lon": -77.5,
    "timezone": "America/New_York",
    "isp": "Google LLC",
    "org": "Google LLC",
    "as": "AS15169 Google LLC",
    "query": MOCK_IP,
}

MOCK_GEO_RESPONSE = GeolocationResponse(
    ip=MOCK_IP,
    country="United States",
    country_code="US",
    region="Virginia",
    city="Ashburn",
    latitude=39.03,
    longitude=-77.5,
    timezone="America/New_York",
    isp="Google LLC",
)


@pytest.fixture
async def api_client() -> AsyncClient:
    """Async test client wired to the FastAPI app via ASGI transport.

    ASGITransport does not trigger the app lifespan, so we manually create
    and inject the HTTP client that the app depends on via app.state.
    """
    async with httpx.AsyncClient(timeout=settings.ip_api_timeout) as http_client:
        app.state.http_client = http_client
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client  # type: ignore[misc]
