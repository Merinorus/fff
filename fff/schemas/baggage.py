from typing import List

from pydantic import BaseModel, NonNegativeInt


class BaggageList(BaseModel):
    """Baggage list PER PASSENGER."""

    checked_bags: NonNegativeInt = 0
    carry_on_bags: NonNegativeInt = 1

    def __str__(self) -> str:
        """Return the baggage information as a string to be added to the website URL.

        Returns:
            str: the baggage information
        """
        parameters: List[str] = []
        if self.checked_bags:
            parameters.append(f"bfc={self.checked_bags}")
        if self.carry_on_bags:
            parameters.append(f"cfc={self.carry_on_bags}")
        return ";".join(parameters)
