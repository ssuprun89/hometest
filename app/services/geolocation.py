import ipaddress

from app.clients.ip_api import IPApiClient
from app.models.geolocation import GeolocationResponse


def _is_local_ip(ip: str) -> bool:
    """Return True if the IP is a loopback, private, or unspecified address.

    Covers 127.0.0.1, localhost, 0.0.0.0, and RFC-1918 private ranges
    (10.x.x.x, 172.16.x.x, 192.168.x.x). These cannot be geolocated by external providers.
    """
    if ip.lower() == "localhost":
        return True
    try:
        addr = ipaddress.ip_address(ip)
        return addr.is_loopback or addr.is_private or addr.is_unspecified
    except ValueError:
        return False


class GeolocationService:
    """Business logic layer for IP geolocation lookups."""

    def __init__(self, client: IPApiClient) -> None:
        self._client = client

    async def get_by_ip(self, ip: str) -> GeolocationResponse:
        """Return geolocation data for the given IP address."""
        return await self._client.get_geolocation(ip)

    async def get_by_client_ip(self, ip: str) -> GeolocationResponse:
        """Return geolocation data for the detected client IP.

        If the IP is local or private (e.g. during local development), delegates IP detection
        to the upstream provider so the developer's public IP is resolved instead.
        """
        if _is_local_ip(ip):
            return await self._client.get_my_geolocation()
        return await self._client.get_geolocation(ip)
