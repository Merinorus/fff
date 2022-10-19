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

    @classmethod
    def from_string(cls, airport_string: str) -> "AirPort":
        """
        Given text extracted from HTML elements, return
        ``AirPort`` instance, which provides a clean airport symbol.
        """
        # Remove leading and trailing spaces
        airport_string = airport_string.strip()
        # Keep the 3 first letters and ensure they are all caps.
        airport_string = airport_string[0:3].upper()
        airport = AirPort(code=airport_string)
        return airport


class AirportTrip(BaseModel):
    """Airport trip search parameters."""

    from_airport: AirPort
    destination_airport: AirPort

    def __str__(self) -> str:
        return f"{self.from_airport}-{self.destination_airport}"
