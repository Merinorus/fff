from pydantic import BaseModel


class AirPort(BaseModel):
    """Airport representation."""

    code: str  # IATA code number, eg: "PAR" for Paris
    allow_nearby_airports: bool = False

    def __str__(self):
        if self.allow_nearby_airports:
            return f"{self.code},nearby"
        else:
            return f"{self.code}"


class AirportRoundTrip(BaseModel):
    """Airport round trip search parameters."""

    from_airport: AirPort
    destination_airport: AirPort

    def __str__(self) -> str:
        return f"{self.from_airport}-{self.destination_airport}"
