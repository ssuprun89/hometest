from typing import Annotated

import httpx
from fastapi import Depends, Path, Request
from pydantic import IPvAnyAddress

from app.clients.ip_api import IPApiClient
from app.services.geolocation import GeolocationService


def get_service(request: Request) -> GeolocationService:
    """FastAPI dependency that constructs a GeolocationService from the shared HTTP client."""
    client: httpx.AsyncClient = request.app.state.http_client
    return GeolocationService(IPApiClient(client))


ServiceDep = Annotated[GeolocationService, Depends(get_service)]
IPV4Type = Annotated[
    IPvAnyAddress, Path(description="IPv4 address to look up", examples=["8.8.8.8"])
]
