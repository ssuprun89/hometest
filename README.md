# IP Geolocation Service

A FastAPI microservice that returns geolocation data for any IPv4 address using [ip-api.com](http://ip-api.com).

---

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — package and environment manager

---

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd hometest

# 2. Install dependencies
make install

# 3. Copy environment config
cp .env.example .env

# 4. Run the service
make run
```

The service starts at **http://localhost:8000**.

---

## Configuration

All settings are read from environment variables or a `.env` file:

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `IP Geolocation Service` | Application title |
| `APP_VERSION` | `1.0.0` | Application version |
| `DEBUG` | `false` | Debug mode |
| `IP_API_BASE_URL` | `http://ip-api.com` | Geolocation provider base URL |
| `IP_API_TIMEOUT` | `10.0` | Upstream request timeout in seconds |

Copy `.env.example` to `.env` and adjust values as needed.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/geolocation/{ip}` | Geolocation for a specific IPv4 address |
| `GET` | `/api/v1/geolocation/me` | Geolocation for the requesting client |

### Example

```bash
curl http://localhost:8000/api/v1/geolocation/8.8.8.8
```

```json
{
  "ip": "8.8.8.8",
  "country": "United States",
  "country_code": "US",
  "region": "Virginia",
  "city": "Ashburn",
  "latitude": 39.03,
  "longitude": -77.5,
  "timezone": "America/New_York",
  "isp": "Google LLC"
}
```

### Error responses

All errors use a consistent format regardless of status code:

```json
{
  "error": "Short error title",
  "detail": "Human-readable explanation"
}
```

| Status | When |
|---|---|
| `422` | Invalid IP format or private/reserved IP address |
| `404` | IP address not found in the geolocation database |
| `503` | Upstream provider is unavailable or timed out |

---

## API Documentation

Interactive docs are available while the service is running:

| Interface | URL |
|---|---|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |

---

## Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# With coverage report
make coverage
```

---

## Code Quality

```bash
# Lint
make lint

# Format
make format

# Type checking
make typecheck

# Run all checks (lint + typecheck + tests)
make check
```

---

## Project Structure

```
app/
├── api/
│   └── v1/
│       ├── dependencies.py      # FastAPI dependencies (service injection, IP type)
│       ├── utils.py             # Client IP extraction from request headers
│       └── routers/
│           └── geolocation.py   # Route handlers
├── clients/
│   └── ip_api.py                # ip-api.com HTTP client
├── core/
│   ├── config.py                # Settings via pydantic-settings
│   └── exceptions.py            # Custom exceptions and error handlers
├── models/
│   ├── geolocation.py           # GeolocationResponse model
│   └── errors.py                # ErrorResponse model
├── services/
│   └── geolocation.py           # Business logic
└── main.py                      # App entrypoint, lifespan, exception handler registration

tests/
├── conftest.py                  # Shared fixtures and mock data
├── unit/                        # Unit tests (service logic, IP extraction)
└── integration/                 # Integration tests (API endpoints, mocked provider)
```

---

## Design Decisions

See [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md) for full reasoning behind:

- API structure and endpoint design
- Choice of ip-api.com as the geolocation provider
- `clients/` layer separation
- Local vs production IP handling for `/me`
- What would be implemented next for production readiness
