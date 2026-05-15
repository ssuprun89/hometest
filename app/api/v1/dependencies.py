from typing import Annotated

from fastapi import Depends, Path, Request
from pydantic import IPvAnyAddress

from app.services.geolocation import GeolocationService


def get_service(request: Request) -> GeolocationService:
    """FastAPI dependency that returns the shared GeolocationService from app state."""
    return request.app.state.geolocation_service  # type: ignore[no-any-return]


ServiceDep = Annotated[GeolocationService, Depends(get_service)]
IPV4Type = Annotated[
    IPvAnyAddress, Path(description="IPv4 address to look up", examples=["8.8.8.8"])
]
