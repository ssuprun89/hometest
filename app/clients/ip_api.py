import httpx

from app.core.config import settings
from app.core.exceptions import (
    GeolocationNotFoundError,
    GeolocationProviderError,
    InvalidIPAddressError,
)
from app.models.geolocation import GeolocationResponse

# Fields requested from ip-api.com — only what we expose in the response model.
_FIELDS = (
    "status,message,country,countryCode,region,regionName,"
    "city,zip,lat,lon,timezone,isp,org,as,query"
)


class IPApiClient:
    """HTTP client wrapper for the ip-api.com geolocation API."""

    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._client = http_client

    async def get_my_geolocation(self) -> GeolocationResponse:
        """Fetch geolocation for the caller's own IP.

        Omits the IP from the URL so ip-api.com resolves the requester's address automatically.
        Used when the service itself is making the request on behalf of a local/private client.
        """
        return await self._fetch(f"{settings.ip_api_base_url}/json/")

    async def get_geolocation(self, ip: str) -> GeolocationResponse:
        """Fetch geolocation for the given IP address."""
        return await self._fetch(f"{settings.ip_api_base_url}/json/{ip}")

    async def _fetch(self, url: str) -> GeolocationResponse:
        """Send a request to ip-api.com and parse the response into a GeolocationResponse.

        Raises:
            GeolocationProviderError: On network errors, timeouts, or unexpected HTTP status codes.
            InvalidIPAddressError: When ip-api.com reports the IP is invalid, private, or reserved.
            GeolocationNotFoundError: When ip-api.com cannot find data for the given IP.
        """
        try:
            response = await self._client.get(url, params={"fields": _FIELDS})
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise GeolocationProviderError("Request to geolocation provider timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise GeolocationProviderError(
                f"Geolocation provider returned HTTP {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise GeolocationProviderError(f"Failed to reach geolocation provider: {exc}") from exc

        data = response.json()

        if data.get("status") == "fail":
            message = data.get("message", "")
            queried_ip = data.get("query", "unknown")
            if message in ("invalid query", "private range", "reserved range"):
                raise InvalidIPAddressError(queried_ip)
            raise GeolocationNotFoundError(queried_ip)

        return GeolocationResponse(
            ip=data["query"],
            country=data["country"],
            country_code=data["countryCode"],
            region=data["regionName"],
            city=data["city"],
            latitude=data["lat"],
            longitude=data["lon"],
            timezone=data["timezone"],
            isp=data["isp"],
        )
