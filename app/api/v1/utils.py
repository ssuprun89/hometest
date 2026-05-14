from fastapi import Request

from app.core.exceptions import GeolocationProviderError


def extract_client_ip(request: Request) -> str:
    """Extract the real client IP from the request.

    Checks proxy headers in order of precedence:
    1. X-Forwarded-For — may contain a comma-separated chain; the first entry is the original
       client.
    2. X-Real-IP — set by nginx and similar reverse proxies.
    3. request.client.host — direct connection fallback.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    if request.client is None:
        raise GeolocationProviderError("Unable to determine client IP address")

    return request.client.host
