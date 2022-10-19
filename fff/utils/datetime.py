from datetime import date, datetime, timedelta
from typing import List

import dateparser
from dateutil.relativedelta import relativedelta
from pydantic import NonNegativeFloat

from fff.config import settings


def hours_to_minutes(time_in_hours: NonNegativeFloat) -> int:
    return round(time_in_hours * 60)


def in_n_days_at_most(from_date: date, nb_days: int, max_date: date) -> date:
    """Returns at most N days later that the "from_date", without exceeding the specified max_date.

    Args:
        from_date (date): The date we start from
        nb_days (int): How many days to add to the date
        max_date (date): the date that should not be excedded

    Returns:
        date: min(N days later from_date, max_date)
    """
    return min(from_date + timedelta(nb_days), max_date)


def split_date_window(start_date: date, end_date: date) -> List[tuple[date, date]]:
    """Split a date window in 5-week long date windows.

    Args:
        start_date (date): start day
        end_date (date): end day

    Returns:
        List[tuple[date, date]]: the splitted date windows as a list
    """
    window_length = 34  # in days
    if (end_date - start_date).days < window_length:
        # Date windows is shorter than 5 weeks, so we return only one date in the list.
        return [(start_date, end_date)]
    else:
        # Date window is longer than 5 weeks so we must split it.
        result: List[tuple[date, date]] = []
        # First window
        split_start_date = start_date
        split_end_date = in_n_days_at_most(
            from_date=split_start_date, nb_days=window_length, max_date=end_date
        )
        result.append((split_start_date, split_end_date))
        while split_end_date < end_date:
            # Move to the next date tuple
            split_start_date = split_end_date + timedelta(days=1)
            split_end_date = in_n_days_at_most(
                from_date=split_start_date, nb_days=window_length, max_date=end_date
            )
            result.append((split_start_date, split_end_date))
        return result


def parse_date(date_str: str) -> datetime:
    date_time = dateparser.parse(date_str, languages=[settings.WEBSITE_LANGUAGE])
    if not date_time:
        raise ValueError(f"Could not parse any date in this string: {date_str}")
    if date_time <= datetime.now():
        # We are PROBABLY at the previous year. TODO Check when we look for trip more than one year ahead.
        # We should instead parse the year written on the calendar on the result page.
        date_time += relativedelta(years=1)
    return date_time
