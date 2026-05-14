# Development Notes

## Implementation Walkthrough

I started by defining the project structure before writing any code. The goal was to establish clear separation of concerns from the beginning rather than refactoring later.

**Order of implementation:**

1. **Project scaffold** — `pyproject.toml`, folder structure (`clients/`, `services/`, `routers/`, `core/`, `models/`), `__init__.py` files
2. **Configuration** — `core/config.py` using `pydantic-settings` to load from environment variables
3. **Models** — `GeolocationResponse` and `ErrorResponse` Pydantic models with full `Field` descriptions to drive the OpenAPI spec
4. **Exceptions** — custom exception classes with dedicated FastAPI handlers, each mapping to a specific HTTP status code
5. **HTTP client** — `clients/ip_api.py` wrapping `httpx.AsyncClient` with all error handling contained in one place
6. **Service layer** — `services/geolocation.py` with the business logic for client IP resolution
7. **Router** — FastAPI endpoints using `IPvAnyAddress` path parameter for built-in format validation
8. **Main app** — lifespan context manager to share a single `httpx.AsyncClient` across requests
9. **Tests** — unit tests first (service logic, IP extraction), then integration tests mocking the external API

---

## Total Time Spent

Approximately **2–3 hours**.

---

## Challenges & Solutions

**Handling `/me` correctly in both local and production environments**

The main challenge was making `GET /geolocation/me` work correctly in two different contexts:

- **Locally**: `request.client.host` is `127.0.0.1`, a private IP that ip-api.com cannot geolocate.
- **In production**: the real client IP is available via `X-Forwarded-For` or `X-Real-IP` headers set by a reverse proxy.

My first approach was to call `ip-api.com/json/` without an IP, letting the provider resolve the caller automatically. This worked locally but would return the server's own IP in production — the opposite of what's needed.

The solution: extract the real client IP from request headers first. If the detected IP is private or local (checked via Python's `ipaddress` module), fall back to calling `ip-api.com/json/` without an IP so the provider resolves it from the outgoing connection. If the IP is public, pass it explicitly to the API. This gives correct behavior in both environments.

**Integration tests with respx and ASGITransport**

`httpx.AsyncClient` with `ASGITransport` does not trigger FastAPI's `lifespan` context manager. This meant `app.state.http_client` was never set during tests, causing `AttributeError` on every request. The fix was to manually create and inject the `httpx.AsyncClient` into `app.state` within the test fixture, bypassing the lifespan entirely for tests. Using `respx.mock` as a context manager inside each test (rather than as a decorator) made the mocking explicit and predictable.

---

## GenAI Usage

I used **Claude Code** throughout this project for:

- **Code generation** — generating boilerplate for models, exception handlers, and test fixtures
- **Code review** — identifying issues like the undefined `ip` variable in `_fetch`, the ordering of `/me` vs `/{ip}` routes, and the missing `__init__.py` files
- **Architectural decisions** — discussing the `clients/` layer separation, the lifespan-vs-dependency-injection trade-off for the HTTP client, and the middleware vs utility function approach for IP extraction

What worked well: Claude was effective at catching subtle bugs (undefined variable in a private method, deprecated API usage) and enforcing consistency (docstrings, type hints, line length). It also saved significant time on test setup boilerplate.

What required human judgement: the `/me` local vs production IP decision required understanding the full deployment context — Claude initially suggested the wrong approach (delegating to the provider unconditionally) until I identified the production flaw.

---

## API Design Decisions

**Why `/api/v1/geolocation/{ip}` and `/api/v1/geolocation/me`?**

- The `/api` prefix leaves room for non-API routes (health checks, admin pages) at the root.
- `/v1` makes versioning explicit from day one. Introducing a breaking change means adding `/v2`, not modifying existing consumers.
- `/geolocation` as a resource noun follows RESTful conventions.
- `/me` is a widely understood convention for "the current authenticated/requesting entity". It is declared before `/{ip}` in the router to prevent FastAPI matching the literal string `"me"` as an IP parameter.

**Why `IPvAnyAddress` for the path parameter?**

Using Pydantic's `IPvAnyAddress` as the path parameter type means FastAPI validates the format before the request reaches the service layer. Invalid formats return a 422 with a structured error immediately, without making an external API call. The validated value is converted to a plain `str` via `.compressed` before passing it to the service, keeping internal layers free of Pydantic types.

**Why a separate `clients/` layer?**

The `IPApiClient` class owns everything related to ip-api.com: URL construction, field selection, HTTP error handling, and response parsing. The `GeolocationService` knows nothing about the external API — it only calls methods on the client. This makes it trivial to swap providers (swap the client, not the service) and to mock in tests (mock the client, not HTTP calls, for unit tests).

**Consistent error format**

All error responses use `{"error": "...", "detail": "..."}` regardless of the status code. This gives API consumers a single parsing pattern for all failure cases.

---

## Third-Party API Selection

**Choice: ip-api.com**

| Criteria | Decision |
|---|---|
| Authentication | Not required — no API key setup or secrets management needed |
| Rate limit | 45 req/min — sufficient for this exercise |
| Data quality | Returns country, region, city, coordinates, timezone, ISP — covers all requirements |
| Ease of integration | Single JSON endpoint, clear `status`/`message` error fields |

**Trade-offs vs a local database (e.g. MaxMind GeoLite2):**

| | ip-api.com | MaxMind GeoLite2 |
|---|---|---|
| Setup | Zero config | Requires download, parsing, scheduled updates |
| Latency | +network RTT (~20–100ms) | Sub-millisecond |
| Rate limits | 45 req/min free | Unlimited |
| Accuracy | High (provider maintains data) | Depends on update frequency |
| Privacy | IP sent to third party | All local, no data leaves the service |
| Cost at scale | Paid plan required | Free (CCPA/GDPR friendly) |

**For production**, a local database is the better choice. It eliminates the external dependency, has no rate limits, is faster, and keeps IP data private. The operational cost (monthly database updates, storage) is low compared to the reliability and latency benefits.

---

## Production Readiness — What I Would Implement Next

1. **Rate limiting** — add a rate limiter (e.g. `slowapi`) to protect the service from abuse and to respect ip-api.com's 45 req/min limit, returning `429 Too Many Requests` with a `Retry-After` header.

2. **Caching** — cache geolocation results by IP in Redis with a TTL (e.g. 24 hours). IP-to-location mappings change rarely; caching would eliminate redundant external API calls and improve response times significantly.

3. **Structured logging** — replace any implicit logging with structured JSON logs (e.g. `structlog`) including request ID, client IP, response time, and upstream API status. Essential for debugging and observability.

4. **Health check endpoint** — `GET /health` returning service status and a liveness check against the upstream provider. Required for Kubernetes liveness/readiness probes and load balancer integration.

5. **Request ID propagation** — generate a UUID per request and attach it to logs and response headers (`X-Request-ID`). Makes distributed tracing and log correlation possible.

6. **Circuit breaker** — wrap the ip-api.com client with a circuit breaker (e.g. `pybreaker`) to fail fast when the upstream is degraded, instead of timing out on every request.

7. **Metrics** — expose Prometheus metrics (request count, latency histogram, upstream error rate, cache hit rate) via `/metrics` for alerting and dashboards.

8. **Switch to a local database** — replace ip-api.com with MaxMind GeoLite2 for production use. Remove the external dependency, eliminate rate limits, reduce latency, and keep IP data on-premise. Automate monthly database updates via a scheduled job.

9. **Authentication** — add API key authentication for service-to-service calls. Even a simple `Authorization: Bearer <token>` header check prevents unauthorized usage and enables per-client rate limiting.

10. **Containerisation and CI** — add a `Dockerfile` (multi-stage build), a `docker-compose.yml` for local development, and a CI pipeline (GitHub Actions) running `make check` on every PR before merge.
