from typing import List

from pydantic import BaseModel, NonNegativeInt, root_validator

# Kayak restriction. Check the night range is 7 nights maximum.
WEBSITE_MAXIMUM_DAY_INTERVAL = 7


class DateWindow(BaseModel):
    """Date window with a maximum of 7 days."""

    min_nights: NonNegativeInt
    max_nights: NonNegativeInt

    @root_validator
    def check_date_window(cls, values):
        if values["max_nights"] < values["min_nights"]:
            raise ValueError(
                f"The maximum amount of nights ({values['max_nights']}) should be above or equal the minimum ({values['min_nights']})."
            )
        elif values["max_nights"] - values["min_nights"] > WEBSITE_MAXIMUM_DAY_INTERVAL:
            raise ValueError(
                f"Please specify a valid number of nights at destination (max. range is {WEBSITE_MAXIMUM_DAY_INTERVAL} nights, got {values['max_nights'] - values['min_nights']} instead.)"
            )
        return values


class FlexibleCalendar(BaseModel):
    """Flexible calendar (list of date windows)"""

    min_nights: NonNegativeInt
    max_nights: NonNegativeInt

    @root_validator
    def check_date_window(cls, values):
        if values["max_nights"] < values["min_nights"]:
            raise ValueError(
                f"The maximum amount of nights ({values['max_nights']}) should be above or equal the minimum ({values['mmin_nights']})."
            )
        return values

    @property
    def date_windows(self) -> List[DateWindow]:
        """
        Split the calendar in 7-day max date windows.

        Returns:
            List[DateWindow]: a list of date windows compatible with Kayak.
        """
        result: List[DateWindow] = list()
        for n in range(
            self.min_nights, self.max_nights, WEBSITE_MAXIMUM_DAY_INTERVAL + 1
        ):
            result.append(
                DateWindow(
                    min_nights=n,
                    max_nights=min(n + WEBSITE_MAXIMUM_DAY_INTERVAL, self.max_nights),
                )
            )
        return result
