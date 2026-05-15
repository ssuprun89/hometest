from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.v1.routers import geolocation
from app.clients.ip_api import IPApiClient
from app.core.config import settings
from app.core.exceptions import (
    GeolocationNotFoundError,
    GeolocationProviderError,
    InvalidIPAddressError,
    invalid_ip_handler,
    not_found_handler,
    provider_error_handler,
    validation_error_handler,
)
from app.services.geolocation import GeolocationService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Create shared resources once at startup and release them at shutdown."""
    http_client = httpx.AsyncClient(timeout=settings.ip_api_timeout)
    app.state.http_client = http_client
    app.state.geolocation_service = GeolocationService(IPApiClient(http_client))
    yield
    await http_client.aclose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A microservice that provides IP address geolocation information.",
    lifespan=lifespan,
)

app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(InvalidIPAddressError, invalid_ip_handler)
app.add_exception_handler(GeolocationNotFoundError, not_found_handler)
app.add_exception_handler(GeolocationProviderError, provider_error_handler)

app.include_router(geolocation.router, prefix="/api/v1")
