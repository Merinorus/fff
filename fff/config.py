"""Configuration variables that can be used accross the FastAPI project."""
import os
from datetime import date
from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings, Field, NonNegativeInt
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

    # Comparator website URL
    WEBSITE_URL: str = "https://www.kayak.fr"

    # Travel preferences
    FROM_AIRPORT: str = "PAR"
    FROM_ALLOW_NEARBY_AIRPORTS: bool = False
    DESTINATION_AIRPORT: str = "YUL"
    DESTINATION_ALLOW_NEARBY_AIRPORTS: bool = False
    MAX_STOPS: MaxNumberOfStops = MaxNumberOfStops.INDIFFERENT
    SEARCH_DATE_BEGIN: date = Field(default=parse_date("2023-01-01"))
    SEARCH_DATE_END: date = Field(default=parse_date("2023-04-01"))
    MIN_NIGHTS: NonNegativeInt = 14
    MAX_NIGHTS: NonNegativeInt = 21

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
