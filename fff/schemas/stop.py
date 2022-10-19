from enum import Enum

from pydantic import BaseModel


class MaxNumberOfStops(Enum):
    INDIFFERENT = -1
    ZERO = 0
    ONE = 1
    TWO_OR_MORE = 2


class MaxStopFilter(BaseModel):
    number_of_stops: MaxNumberOfStops = MaxNumberOfStops.INDIFFERENT

    def __str__(self) -> str:
        """Return the stop filter to be added to the search URL."""
        if self.number_of_stops == MaxNumberOfStops.ZERO:
            return "stops=~0"
        elif self.number_of_stops == MaxNumberOfStops.ONE:
            return "stops=-2"
        else:
            return ""
