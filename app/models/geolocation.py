from pydantic import BaseModel, Field


class GeolocationResponse(BaseModel):
    """Geolocation data returned for a resolved IP address."""

    ip: str = Field(description="The queried IP address", examples=["8.8.8.8"])
    country: str = Field(description="Full country name", examples=["United States"])
    country_code: str = Field(description="ISO 3166-1 alpha-2 country code", examples=["US"])
    region: str = Field(description="Region or state name", examples=["Virginia"])
    city: str = Field(description="City name", examples=["Ashburn"])
    latitude: float = Field(description="Latitude coordinate", examples=[39.03])
    longitude: float = Field(description="Longitude coordinate", examples=[-77.5])
    timezone: str = Field(description="IANA timezone identifier", examples=["America/New_York"])
    isp: str = Field(description="Internet Service Provider name", examples=["Google LLC"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ip": "8.8.8.8",
                    "country": "United States",
                    "country_code": "US",
                    "region": "Virginia",
                    "city": "Ashburn",
                    "latitude": 39.03,
                    "longitude": -77.5,
                    "timezone": "America/New_York",
                    "isp": "Google LLC",
                }
            ]
        }
    }
