from fff.schemas.flexible_calendar import DateWindow, FlexibleCalendar


def test_flexible_calendar():
    """Check that a calendar is correctly splitted into date windows."""
    calendar = FlexibleCalendar(min_nights=10, max_nights=30)
    assert calendar.date_windows == [
        DateWindow(min_nights=10, max_nights=17),
        DateWindow(min_nights=18, max_nights=25),
        DateWindow(min_nights=26, max_nights=30),
    ]
