from pydantic import BaseModel, Field, NonNegativeFloat

from fff.utils.datetime import hours_to_minutes


class LayoverFilter(BaseModel):
    min_time: NonNegativeFloat = Field(
        ..., description="Minimum duration of the layover, in hours"
    )
    max_time: NonNegativeFloat = Field(
        ..., description="Maximum duration of the layover, in hours"
    )

    def __str__(self) -> str:
        """Return the layover duration filter to be added to the search URL."""

        if self.min_time == 0 and self.max_time == 0:
            return ""
        elif self.min_time == 0 and self.max_time > 0:
            return f"layoverdur=-{hours_to_minutes(self.max_time)}"
        elif self.max_time < self.min_time:
            raise ValueError(
                "Maximum layover duration should be higher than minimum layover duration."
            )
        else:
            return f"layoverdur={hours_to_minutes(self.min_time)}-{hours_to_minutes(self.max_time)}"
