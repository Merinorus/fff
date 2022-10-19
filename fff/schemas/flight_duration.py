from pydantic import BaseModel, Field, NonNegativeFloat

from fff.utils.datetime import hours_to_minutes


class FlightDurationFilter(BaseModel):
    max_time: NonNegativeFloat = Field(
        ..., description="Maximum duration of the flight, in hours"
    )

    def __str__(self) -> str:
        """Return the flight duration filter to be added to the search URL."""

        if self.max_time == 0:
            return ""
        else:
            return f"legdur=-{hours_to_minutes(self.max_time)}"
