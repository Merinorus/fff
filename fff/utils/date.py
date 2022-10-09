from datetime import date, timedelta
from typing import List


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
