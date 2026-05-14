from fastapi import Request
from fastapi.responses import JSONResponse


class InvalidIPAddressError(Exception):
    """Raised when an IP is syntactically invalid or cannot be geolocated (private/reserved)."""

    def __init__(self, ip: str) -> None:
        self.ip = ip
        super().__init__(
            f"{ip!r} is not a valid or geolocatable IP address "
            f"(private/reserved ranges are not supported)"
        )


class GeolocationNotFoundError(Exception):
    """Raised when the geolocation provider has no data for the given IP."""

    def __init__(self, ip: str) -> None:
        self.ip = ip
        super().__init__(f"Geolocation data not found for IP {ip!r}")


class GeolocationProviderError(Exception):
    """Raised when the upstream geolocation API is unreachable or returns an unexpected error."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


async def invalid_ip_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle InvalidIPAddressError and return HTTP 422."""
    assert isinstance(exc, InvalidIPAddressError)
    return JSONResponse(
        status_code=422,
        content={"error": "Invalid IP address", "detail": str(exc)},
    )


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle GeolocationNotFoundError and return HTTP 404."""
    assert isinstance(exc, GeolocationNotFoundError)
    return JSONResponse(
        status_code=404,
        content={"error": "Geolocation not found", "detail": str(exc)},
    )


async def provider_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle GeolocationProviderError and return HTTP 503."""
    assert isinstance(exc, GeolocationProviderError)
    return JSONResponse(
        status_code=503,
        content={"error": "Geolocation provider unavailable", "detail": str(exc)},
    )
