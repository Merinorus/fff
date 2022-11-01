import html
from datetime import date, datetime
from time import sleep
from typing import List, Union
from urllib.parse import urljoin

from price_parser import Price
from pydantic import BaseModel, HttpUrl
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from fff.config import settings
from fff.schemas.airport import AirPort, AirportTrip
from fff.schemas.baggage import BaggageList
from fff.schemas.flight_duration import FlightDurationFilter
from fff.schemas.flight_search import FlightSearchParameters
from fff.schemas.layover import LayoverFilter
from fff.schemas.passenger import PassengerList
from fff.schemas.stop import MaxStopFilter
from fff.utils.datetime import parse_date, split_date_window
from fff.utils.logging import logger
from fff.utils.progress_bar import progressbar_is_full


class UrlGenerator:
    def __init__(self):
        self.passenger_list = PassengerList(
            adults=settings.PASSENGER_ADULTS,
            children=settings.PASSENGER_CHILDREN,
            infant_on_lap=settings.PASSENGER_INFANTS_ON_LAP,
            seniors=settings.PASSENGER_SENIORS,
            students=settings.PASSENGER_STUDENTS,
            toddlers_in_seat=settings.PASSENGER_TODDLERS_IN_OWN_SEAT,
            youths=settings.PASSENGER_YOUTHS,
        )
        self.baggage_list = BaggageList(
            checked_bags=settings.CHECKED_BAG_PER_PASSENGER,
            carry_on_bags=settings.CARRY_ON_BAG_PER_PASSENGER,
        )
        self.max_stop_filter = MaxStopFilter(number_of_stops=settings.MAX_STOPS)
        self.flight_duration_filter = FlightDurationFilter(
            max_time=settings.MAX_FLIGHT_DURATION
        )
        self.layover_filter = LayoverFilter(
            min_time=settings.MIN_LAYOVER_DURATION,
            max_time=settings.MAX_LAYOVER_DURATION,
        )
        self.search_parameters = FlightSearchParameters(
            passenger_list=self.passenger_list,
            baggage_list=self.baggage_list,
            max_stop_filter=self.max_stop_filter,
            layover_filter=self.layover_filter,
            flight_duration_filter=self.flight_duration_filter,
        )
        self.date_tuples = split_date_window(
            settings.SEARCH_DATE_BEGIN, settings.SEARCH_DATE_END
        )

        self.from_airport = AirPort(
            code=settings.FROM_AIRPORT,
            allow_nearby_airports=settings.FROM_ALLOW_NEARBY_AIRPORTS,
        )
        self.destination_airport = AirPort(
            code=settings.DESTINATION_AIRPORT,
            allow_nearby_airports=settings.DESTINATION_ALLOW_NEARBY_AIRPORTS,
        )
        self.round_trip = AirportTrip(
            from_airport=self.from_airport, destination_airport=self.destination_airport
        )

    @property
    def date_begin(self) -> date:
        return self.date_tuples[0][0]

    @property
    def date_end(self) -> date:
        return self.date_tuples[-1][1]

    def generate_url(
        self, start_date: date, end_date: date, flexible_calendar: bool = True
    ) -> str:
        """
        Generate the search URL for a given date.

        Returns:
            str: The URL
        """
        url = f"{settings.WEBSITE_URL}/flights/{self.round_trip}/{start_date.isoformat()}/{end_date.isoformat()}"
        if flexible_calendar:
            url = (
                url + f"-flexible-calendar-{settings.MIN_NIGHTS}to{settings.MAX_NIGHTS}"
            )
        url = url + str(self.search_parameters)
        return url

    def generate_urls(self, flexible_calendar: bool = True) -> List[str]:
        """Generate the list of URL to scrap

        Returns:
            List[str]: The list of URLs
        """

        urls: List[str] = []
        for start_date, end_date in self.date_tuples:
            url = self.generate_url(start_date, end_date, flexible_calendar)
            logger.debug(f"Adding URL: {url}")
            urls.append(url)
        return urls


class FlightDateElement(BaseModel):
    web_element: WebElement
    price: Price

    class Config:
        arbitrary_types_allowed = True

    def __repr__(self):
        return f"Flight: {self.price.amount}"


class FlightTrip(BaseModel):
    search_link: Union[HttpUrl, None]  # Search link for other flights at this date
    direct_link: Union[HttpUrl, None]  # Direct link to the selling company
    first_trip: Union[AirportTrip, None]
    first_trip_date: datetime | None
    return_trip: Union[AirportTrip, None]
    return_trip_date: datetime | None
    price: Price = Price.fromstring("100 €")

    class Config:
        arbitrary_types_allowed = True

    def __repr__(self):
        return f"### Flight trip {self.first_trip.from_airport}-{self.first_trip.destination_airport} at {self.first_trip_date.date().isoformat()}, return {self.return_trip.from_airport}-{self.return_trip.destination_airport} at {self.return_trip_date.date().isoformat()}, price {self.price.currency}{self.price.amount_text} ###\n#\n# Booking link: {self.direct_link}\n#\n# Other flights at this date:{self.search_link}\n###"

    def __str__(self):
        return self.__repr__()


class Bot:
    def __init__(self):
        self.default_timeout = 10
        options = webdriver.FirefoxOptions()
        options.headless = settings.HEADLESS_MODE
        # Use Firefox browser (geckodriver)
        self.driver: webdriver.Remote = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(self.default_timeout)
        self.started = False
        self.search_urls: List[str] | None = None
        self.url_generator = UrlGenerator()

    def _force_click(self, element: WebElement):
        """Replace classical Selenium click when the latter is not possible.

        Args:
            element (WebElement): The web element to click on
        """
        self.driver.execute_script("arguments[0].click();", element)

    def _remove(self, element: WebElement) -> None:
        """Remove f web element from the DOM.

        Args:
            element (WebElement): the web element to remove
        """
        self.driver.execute_script("arguments[0].remove();", element)

    def _click_outside(self):
        """Click on a blank area.

        May be used to make a popup disappear."""
        self.driver.find_element(By.XPATH, "//html").click()

    def _press_key(self, key: str = Keys.NULL) -> None:
        """Press a key in the bot web browser

        Args:
            key (Keys): The key to press on. Keycodes available in module selenium.webdriver.common.keys.Keys
        """
        webdriver.ActionChains(self.driver).send_keys(key).perform()

    def revert_default_timeout(self):
        self.driver.implicitly_wait(self.default_timeout)

    def hide_cookies_disclaimer(self):
        try:
            buttons = self.driver.find_elements(
                By.XPATH, "//span[contains(@class, 'decline')]"
            )
            for button in buttons:
                button.click()
            logger.debug("Closed the cookie disclaimer")
        except NoSuchElementException as e:
            logger.info(
                "Cookies disclaimer not found. The website CSS may have changed or your country does not belong to the cookies disclaimer politic."
            )
            logger.exception(e)

    def start(self):
        self.driver.get(settings.WEBSITE_URL)
        self.hide_cookies_disclaimer()
        self.started = True

    def wait_progress_bar(self):
        """Wait for the website progress bar to finish (if there is one)."""
        header_containing_progress_bar = self.driver.find_element(
            By.XPATH, "//div[contains(@class, '-pres-inline')]"
        )
        progressbar_xpath = (
            '//div[contains(@class, "progress")]/*/div[contains(@class, "bar")]'
        )
        try:
            self.driver.implicitly_wait(3)
            if header_containing_progress_bar.find_element(By.XPATH, progressbar_xpath):
                browser_wait = WebDriverWait(self.driver, 60)
                browser_wait.until(progressbar_is_full((By.XPATH, progressbar_xpath)))
        except NoSuchElementException:
            # There is no progress bar. The website had already cached results
            pass
        self.revert_default_timeout()

    def _get_best_dates(
        self, web_element: WebElement, nb_results: int
    ) -> List[FlightDateElement]:
        flight_date_webelements = web_element.find_elements(
            By.XPATH, "//div[@class='price']"
        )
        flight_dates: List[FlightDateElement] = []

        for web_element in flight_date_webelements:
            try:
                raw_price = web_element.text
                # Make sure the departure date case is not empty
                if raw_price:
                    price = Price.fromstring(raw_price)
                    if price.amount:
                        flight_dates.append(
                            FlightDateElement(
                                web_element=web_element,
                                price=price,
                            )
                        )
            except StaleElementReferenceException as e:
                logger.exception(e)
        flight_dates.sort(key=lambda x: x.price)
        chosen_dates = flight_dates[0:nb_results]
        return chosen_dates

    def _get_best_departure_dates(
        self, url: str, nb_results: int
    ) -> List[FlightDateElement]:
        self.driver.get(url)
        self.wait_progress_bar()

        return self._get_best_dates(
            web_element=self.driver.find_element(By.XPATH, "//html"),
            nb_results=nb_results,
        )

    def get_best_flights(self, url: str, nb_results: int) -> List[FlightTrip]:
        # Add a margin in case they are several dates with the same price
        margin = 2
        departure_dates: List[FlightDateElement] = self._get_best_departure_dates(
            url, nb_results + margin
        )
        result: List[FlightTrip]
        result = []
        # logger.debug(f"{departure_dates=}")
        for d in departure_dates:
            self._force_click(d.web_element)
            sleep(1)
            self._press_key(Keys.ESCAPE)

        sleep(1.5)
        return_result_list: List[WebElement] = self.driver.find_elements(
            By.XPATH, "//div[@class='returnResultItem']"
        )

        # For each departure date, there is a return result list.
        for return_result_item in return_result_list:
            try:
                # Check all return results in the list
                flight_trip = FlightTrip()

                # Parse price
                price_web_element = return_result_item.find_element(
                    By.XPATH, ".//span[@class='price-text']"
                )

                flight_trip.price = Price.fromstring(
                    price_web_element.get_attribute("textContent")
                )

                # Parse dates
                date_webelements = return_result_item.find_elements(
                    By.XPATH, ".//div[contains(@class, 'with-date')]"
                )
                date_first_trip_webelement = date_webelements[0]
                date_first_trip = parse_date(
                    date_first_trip_webelement.get_attribute("textContent")
                )
                flight_trip.first_trip_date = date_first_trip
                date_return_trip_webelement = date_webelements[1]

                date_return_trip = parse_date(
                    date_return_trip_webelement.get_attribute("textContent")
                )
                flight_trip.return_trip_date = date_return_trip

                # Parse booking link
                booking_link_web_element = return_result_item.find_element(
                    By.XPATH, ".//a[@class='booking-link ']"
                )
                booking_link = booking_link_web_element.get_attribute("href")
                escaped_booking_link = html.unescape(booking_link)
                flight_trip.direct_link = urljoin(
                    settings.WEBSITE_URL, escaped_booking_link
                )

                # For search link, we need departure date, return date and airports
                first_trip_from_airport_str = return_result_item.find_element(
                    By.XPATH, ".//div[contains(@id, 'leg-0-origin-airport')]"
                ).get_attribute("textContent")
                first_trip_to_airport_str = return_result_item.find_element(
                    By.XPATH, ".//div[contains(@id, 'leg-0-destination-airport')]"
                ).get_attribute("textContent")
                flight_trip.first_trip = AirportTrip(
                    from_airport=AirPort.from_string(first_trip_from_airport_str),
                    destination_airport=AirPort.from_string(first_trip_to_airport_str),
                )

                return_trip_from_airport_str = return_result_item.find_element(
                    By.XPATH, ".//div[contains(@id, 'leg-1-origin-airport')]"
                ).get_attribute("textContent")

                return_trip_to_airport_str = return_result_item.find_element(
                    By.XPATH, ".//div[contains(@id, 'leg-1-destination-airport')]"
                ).get_attribute("textContent")
                flight_trip.return_trip = AirportTrip(
                    from_airport=AirPort.from_string(return_trip_from_airport_str),
                    destination_airport=AirPort.from_string(return_trip_to_airport_str),
                )

                flight_trip.search_link = self.url_generator.generate_url(
                    date_first_trip.date(),
                    date_return_trip.date(),
                    flexible_calendar=False,
                )

                # Add the trip to the list
                if flight_trip.return_trip_date.date() < self.url_generator.date_end:
                    result.append(flight_trip)
                else:
                    # "Flight trip not added because return date exceeds the maximum specified date."
                    pass
            except StaleElementReferenceException as e:
                logger.exception(e)

        result.sort(key=lambda x: x.price)
        result = result[0:nb_results]
        logger.debug(f"Found {len(result)} flight(s) for this URL.")
        return result

    def search(self):
        if not self.started:
            self.start()

        self.search_urls = self.url_generator.generate_urls()

        self.results: List[FlightTrip]
        self.results = []

        for i, url in enumerate(self.search_urls):
            print(f"Scraping the website... [URL {i+1}/{len(self.search_urls)}]")
            flight_trips = self.get_best_flights(
                url, nb_results=settings.NUMBER_OF_RESULTS
            )
            self.results.extend(flight_trips)

        self.results.sort(key=lambda x: x.price)
        self.results = self.results[0 : settings.NUMBER_OF_RESULTS]
        print(
            f"Here are the {len(self.results)} cheapest flights matching your criterias:\n\n"
            + "\n\n".join([str(result) for result in self.results])
            + "\n\nDone!"
        )
