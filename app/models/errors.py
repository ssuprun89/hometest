from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Consistent error response returned for all API error cases."""

    error: str
    detail: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"error": "Invalid IP address", "detail": "192.168.1.999 is not a valid IP address"}
            ]
        }
    }
