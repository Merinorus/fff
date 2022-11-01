"""Configuration variables that can be used accross the FastAPI project."""
import os
from datetime import date
from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings, Field, NonNegativeFloat, NonNegativeInt
from pydantic.datetime_parse import parse_date

from fff.schemas.stop import MaxNumberOfStops

# Project root directory
PROJECT_DIR = Path((os.path.dirname(__file__))).resolve().parent


class Settings(BaseSettings):
    """
    Application settings. Can be overriden by environment variables.
    """

    APP_NAME: str = "Flexible Flight Finder"
    APP_DESCRIPTION: str = "Find the cheapest flight with more flexible dates than online flight comparators."

    # Application log level. Can be any python log level: NOTSET, DEBUG, INFO, WARNING, ERROR, FATAL.
    LOG_LEVEL: str = "INFO"

    HEADLESS_MODE: bool = True  # Run without browser GUI

    # Comparator website URL
    WEBSITE_LANGUAGE: str = "fr"
    WEBSITE_URL: str = "https://www.kayak.fr"
    NUMBER_OF_RESULTS: NonNegativeInt = 3  # How many flight search results to keep

    # Travel preferences
    FROM_AIRPORT: str = "PAR"
    FROM_ALLOW_NEARBY_AIRPORTS: bool = False
    DESTINATION_AIRPORT: str = "YUL"
    DESTINATION_ALLOW_NEARBY_AIRPORTS: bool = False
    MAX_STOPS: int = MaxNumberOfStops.INDIFFERENT.value
    SEARCH_DATE_BEGIN: date = Field(default=parse_date("2023-01-01"))
    SEARCH_DATE_END: date = Field(default=parse_date("2023-04-01"))
    MIN_NIGHTS: NonNegativeInt = 14
    MAX_NIGHTS: NonNegativeInt = 21

    MAX_FLIGHT_DURATION: NonNegativeFloat = 240  # in hours

    MIN_LAYOVER_DURATION: NonNegativeFloat = 0  # In hours. "Escale"
    MAX_LAYOVER_DURATION: NonNegativeFloat = 72

    PASSENGER_ADULTS: NonNegativeInt = 1  # 18 <= age < 65
    PASSENGER_STUDENTS: NonNegativeInt = 0  # >= 18 years old
    PASSENGER_SENIORS: NonNegativeInt = 0  # >= 65 years old
    PASSENGER_YOUTHS: NonNegativeInt = 0  # 12 <= age <= 17
    PASSENGER_CHILDREN: NonNegativeInt = 0  # 2 <= age <= 11
    PASSENGER_TODDLERS_IN_OWN_SEAT: NonNegativeInt = 0  # <= 2 years old
    PASSENGER_INFANTS_ON_LAP: NonNegativeInt = 0  # <= 2 years old

    CARRY_ON_BAG_PER_PASSENGER: NonNegativeInt = 1
    CHECKED_BAG_PER_PASSENGER: NonNegativeInt = 0

    # The variables can be overriden by the environment file
    class Config:
        env_file = ".env"
        case_sensitive = True
        use_enum_values = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get the settings on demand, all across the project.

    Getting the settings via a function is a dependency injection to facilitate testing.
    LRU cached to avoid reading the .env file at every call.
    """
    settings = Settings()

    # Kayak restriction. Check the night range is 7 nights maximum.
    if settings.MAX_NIGHTS - settings.MIN_NIGHTS > 7:
        raise ValueError(
            "Please specify a valid number of nights at destination (max. range is 7 nights e.g. 14-21)."
        )

    return settings


settings = get_settings()
