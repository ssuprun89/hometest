from fastapi import APIRouter, Request

from app.api.v1.dependencies import IPV4Type, ServiceDep
from app.api.v1.utils import extract_client_ip
from app.models.errors import ErrorResponse
from app.models.geolocation import GeolocationResponse

router = APIRouter(prefix="/geolocation", tags=["Geolocation"])


@router.get(
    "/me",
    response_model=GeolocationResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Geolocation data not found for detected IP"},
        422: {"model": ErrorResponse, "description": "Client IP is private or reserved"},
        503: {"model": ErrorResponse, "description": "Geolocation provider unavailable"},
    },
    summary="Get geolocation for the requesting client",
    description=(
        "Detects the caller's IP address from the request and returns its geolocation data. "
        "Resolves the real client IP from `X-Forwarded-For` or `X-Real-IP` headers "
        "when behind a proxy."
    ),
)
async def get_my_geolocation(request: Request, service: ServiceDep) -> GeolocationResponse:
    """Return geolocation for the client making the request."""
    ip = extract_client_ip(request)
    return await service.get_by_client_ip(ip)


@router.get(
    "/{ip}",
    response_model=GeolocationResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Geolocation data not found for the given IP"},
        422: {"model": ErrorResponse, "description": "Invalid IP address format"},
        503: {"model": ErrorResponse, "description": "Geolocation provider unavailable"},
    },
    summary="Get geolocation for a specific IP address",
    description="Returns geolocation data for the given IPv4 address.",
)
async def get_ip_geolocation(ip: IPV4Type, service: ServiceDep) -> GeolocationResponse:
    """Return geolocation for the specified IP address."""
    return await service.get_by_ip(ip.compressed)
