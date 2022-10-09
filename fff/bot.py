from typing import List
from urllib.parse import urljoin

from price_parser import Price
from pydantic import BaseModel, HttpUrl
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from fff.config import settings
from fff.schemas.airport import AirPort, AirportRoundTrip
from fff.schemas.baggage import BaggageList
from fff.schemas.flight_search import FlightSearchParameters
from fff.schemas.passenger import PassengerList
from fff.schemas.stop import MaxStopFilter
from fff.utils.date import split_date_window
from fff.utils.logging import logger
from fff.utils.progress_bar import progressbar_is_full


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
    search_link: HttpUrl  # Search link for other flights at this date
    direct_link: HttpUrl  # Direct link to the selling company
    # price: PositiveInt
    # currency: str
    price: Price

    class Config:
        arbitrary_types_allowed = True


class Bot:
    def __init__(self):
        # Use Firefox without GUI
        self.default_timeout = 10
        options = webdriver.FirefoxOptions()
        options.headless = False
        self.driver: webdriver.Remote = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(self.default_timeout)
        self.started = False
        self.search_urls: List[str] | None = None

    def _force_click(self, element: WebElement):
        """Replace classical Selenium click when the latter is not possible.

        Args:
            element (WebElement): The web element to click on
        """
        self.driver.execute_script("arguments[0].click();", element)

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
            raw_price = web_element.text
            # Make sure the departure date case is not empty
            if raw_price:
                # logger.debug(f"{raw_price=}")
                price = Price.fromstring(raw_price)
                if price.amount:
                    # logger.debug(f"Price: {price}")
                    flight_dates.append(
                        FlightDateElement(
                            web_element=web_element,
                            price=price,
                        )
                    )
        # logger.debug(f"{flight_dates=}")
        flight_dates.sort(key=lambda x: x.price)
        # logger.debug(f"{flight_dates=}")
        chosen_dates = flight_dates[0:nb_results]
        return chosen_dates

    def _get_best_departure_dates(
        self, url: str, nb_results: int
    ) -> List[FlightDateElement]:
        self.driver.get(url)
        self.wait_progress_bar()

        # departure_dates_webelements = self.driver.find_elements(
        #     By.XPATH, "//div[@class='price']"
        # )
        # departure_dates: List[FlightDateElement] = []

        # for web_element in departure_dates_webelements:
        #     raw_price = web_element.text
        #     # Make sure the departure date case is not empty
        #     if raw_price:
        #         logger.debug(f"{raw_price=}")
        #         price = Price.fromstring(raw_price)
        #         if price.amount:
        #             logger.debug(f"Price: {price}")
        #             departure_dates.append(
        #                 FlightDateElement(web_element=web_element, price=price.amount)
        #             )
        # departure_dates.sort(key=lambda x: x.price)
        # chosen_dates = departure_dates[0 : nb_results - 1]
        # return chosen_dates
        return self._get_best_dates(
            web_element=self.driver.find_element(By.XPATH, "//html"),
            nb_results=nb_results,
        )

    def get_best_flights(self, url: str, nb_results: int) -> List[FlightTrip]:
        departure_dates: List[FlightDateElement] = self._get_best_departure_dates(
            url, nb_results
        )
        result: List[FlightTrip] = []
        for d in departure_dates:
            self._force_click(d.web_element)
            # Clicking on a departure date open a dialog content with return dates
            return_dialog = self.driver.find_element(
                By.XPATH, "//div[contains(@class, 'returnView')]"
            )
            return_dates = self._get_best_dates(return_dialog, nb_results)
            logger.debug(f"{return_dates=}")
            # self.driver.implicitly_wait(1)
            for return_date in return_dates:
                logger.debug("New loop: trying to check the return date results")
                # Try to check the result. Sometimes click doesn't work?
                result_details = None

                # self._force_click(return_date.web_element)
                return_date.web_element.click()
                result_detail_candidates: List[
                    WebElement
                ] = return_dialog.find_elements(
                    By.XPATH,
                    # "//div[contains(@class, 'resultVisible') and not(ancestor::div[contains(@style,'display:none')])]",
                    "//div[contains(@class, 'resultVisible')]",
                )
                logger.debug(f"{result_detail_candidates=}")
                for elem in result_detail_candidates:
                    if elem.is_displayed():
                        logger.debug("displayed element")
                        result_details = elem

                if not result_details:
                    logger.warning("Failed to load a result for a return date.")
                else:
                    search_link = result_details.find_element(
                        By.XPATH, "//a[contains(@class, 'searchMore')]"
                    ).get_attribute("href")

                    direct_link = result_details.find_element(
                        By.XPATH, "//a[contains(@class, 'booking-link')]"
                    ).get_attribute("href")
                    flight_trip = FlightTrip(
                        search_link=urljoin(settings.WEBSITE_URL, search_link),
                        direct_link=direct_link,
                        price=return_date.price,
                    )
                    result.append(flight_trip)
                    logger.debug("Appended flight trip to the results.")
                # Quite the current popup
                self._press_key(Keys.ESCAPE)
                # self.driver.refresh()
                # self._click_outside()
        # self.revert_default_timeout()
        return result

    def search(self):
        if not self.started:
            self.start()

        self.search_urls = generate_urls()

        # TODO do all urls
        flight_trips = self.get_best_flights(
            self.search_urls[0], nb_results=settings.NUMBER_OF_RESULTS
        )
        for trip in flight_trips:
            logger.info(f"{trip=}")
        # for url in self.search_urls:
        #     self.get_best_flights(url, nb_results=settings.NUMBER_OF_RESULTS)

        # TODO
        # For each url
        # - Get N cheapest two-direction flight
        # - store in global array
        # At the end
        # Keep N best flights from array
        # - show flight description & URL
