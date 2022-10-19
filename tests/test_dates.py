from datetime import date

from fff.bot import split_date_window


def test_split_date():
    """Check that a date is splitten in 5-week long windows."""
    start_date = date(2022, 1, 1)
    end_date = date(2022, 3, 31)
    result = split_date_window(start_date, end_date)
    assert result == [
        (date(2022, 1, 1), date(2022, 2, 4)),
        (date(2022, 2, 5), date(2022, 3, 11)),
        (date(2022, 3, 12), date(2022, 3, 31)),
    ]
