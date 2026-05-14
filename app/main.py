from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.v1.routers import geolocation
from app.core.config import settings
from app.core.exceptions import (
    GeolocationNotFoundError,
    GeolocationProviderError,
    InvalidIPAddressError,
    invalid_ip_handler,
    not_found_handler,
    provider_error_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Manage the lifecycle of the shared HTTP client.

    A single AsyncClient is created at startup and closed at shutdown,
    allowing connection pooling across all requests.
    """
    app.state.http_client = httpx.AsyncClient(timeout=settings.ip_api_timeout)
    yield
    await app.state.http_client.aclose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A microservice that provides IP address geolocation information.",
    lifespan=lifespan,
)

app.add_exception_handler(InvalidIPAddressError, invalid_ip_handler)
app.add_exception_handler(GeolocationNotFoundError, not_found_handler)
app.add_exception_handler(GeolocationProviderError, provider_error_handler)

app.include_router(geolocation.router, prefix="/api/v1")
