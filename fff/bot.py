from datetime import date, timedelta
from typing import List

from selenium import webdriver

from fff.config import settings
from fff.schemas.airport import AirPort, AirportRoundTrip
from fff.schemas.baggage import BaggageList
from fff.schemas.flight_search import FlightSearchParameters
from fff.schemas.passenger import PassengerList
from fff.schemas.stop import MaxStopFilter
from fff.utils.logging import logger


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


def generate_urls() -> List[str]:
    """Generate the list of URL to scrap

    Returns:
        List[str]: The list of URLs
    """
    passenger_list = PassengerList(
        adults=settings.PASSENGER_ADULTS,
        children=settings.PASSENGER_CHILDREN,
        infant_on_lap=settings.PASSENGER_INFANTS_ON_LAP,
        seniors=settings.PASSENGER_SENIORS,
        students=settings.PASSENGER_STUDENTS,
        toddlers_in_seat=settings.PASSENGER_TODDLERS_IN_OWN_SEAT,
        youths=settings.PASSENGER_YOUTHS,
    )
    baggage_list = BaggageList(
        checked_bags=settings.CHECKED_BAG_PER_PASSENGER,
        carry_on_bags=settings.CARRY_ON_BAG_PER_PASSENGER,
    )
    max_stop_filter = MaxStopFilter(number_of_stops=settings.MAX_STOPS)
    search_parameters = FlightSearchParameters(
        passenger_list=passenger_list,
        baggage_list=baggage_list,
        max_stop_filter=max_stop_filter,
    )
    date_tuples = split_date_window(
        settings.SEARCH_DATE_BEGIN, settings.SEARCH_DATE_END
    )
    from_airport = AirPort(
        code=settings.FROM_AIRPORT,
        allow_nearby_airports=settings.FROM_ALLOW_NEARBY_AIRPORTS,
    )
    destination_airport = AirPort(
        code=settings.DESTINATION_AIRPORT,
        allow_nearby_airports=settings.DESTINATION_ALLOW_NEARBY_AIRPORTS,
    )
    round_trip = AirportRoundTrip(
        from_airport=from_airport, destination_airport=destination_airport
    )

    urls: List[str] = []
    for start_date, end_date in date_tuples:
        url = f"{settings.WEBSITE_URL}/flights/{round_trip}/{start_date.isoformat()}/{end_date.isoformat()}-flexible-calendar-{settings.MIN_NIGHTS}to{settings.MAX_NIGHTS}{search_parameters}"
        urls.append(url)
    return urls


class Bot:
    def __init__(self):
        # Use Firefox without GUI
        options = webdriver.FirefoxOptions()
        options.headless = False
        self.driver: webdriver.Remote = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)

    def start(self):

        urls = generate_urls()
        for url in urls:
            logger.debug(f"Will get URL: {url}")
        # TODO
        # For each url
        # - Get N cheapest two-direction flight
        # - store in global array
        # At the end
        # Keep N best flights from array
        # - show flight description & URL
