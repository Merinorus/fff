# fff - the Flexible Flight Finder

Find the cheapest round-trip flight with more flexible dates than online flight comparators.

## Features

FFF is a command-line interface to help scraping Kayak's round trips with the [flexible date](https://www.kayak.com/news/flexible-dates-nearby-airports/) mode only.

A round-trip search on Kayak is done as following:

- Specify 🛫 **source** and 🛬**destination** airports
- 🛌**How many nights** you want to stay (eg: between 12 and 15 nights)
- 🗓️The **travel period** (eg: January 2023)

**But there are some limitations on Kayak**:

- You cannot specify an interval duration higher that 7 days (eg: you cannot search a trip between 10 and 20 days)
- The search period is limited to 4 weeks (eg: you cannot look for a flight from january to mars)

**This tool removes these limits!**

## How to run

### Natively with Python (Windows, MacOS, Linux)

Requirements:

- [Python 3.10](https://www.python.org/downloads/)
- [Mozilla Firefox](https://www.mozilla.org/firefox)
- [Geckodriver](https://github.com/mozilla/geckodriver/releases)

```python
> pip install -r requirements.txt
> python -m fff
```

### With Docker

```shell
> docker-compose up --build
```

## Configuration

The configuration is located at `fff/config.py`.
You can override any of the settings with a `.env` file at the project root directory (or just pass the environment variables to Docker if you're using it).

An [`example.env`](./example.env) file is available to help you writing your own trip.

You can configure the application with the following [environment variables](https://en.wikipedia.org/wiki/Environment_variable):

- **`LOG_LEVEL`**: Application log level. Can be any python log level: `NOTSET`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `FATAL`.<br/>
    Default: `INFO`

- **`HEADLESS_MODE`**: Run without browser GUI (this bot is based on [Selenium](https://github.com/SeleniumHQ/selenium)). You can set it to `false` for debugging purposes.<br/>
    Default: `true`

- **`WEBSITE_URL`**: The Kayak website you want to search on, especially depending on the currency you expect.<br/>
    Default: `https://www.kayak.com`

- **`WEBSITE_LANGUAGE`**: Set it accordigly to the **`WEBSITE_URL`** variable. This is needed to parse dates correctly.<br/>
    Default: `en`
- **`NUMBER_OF_RESULTS`**: The N cheapest results you want.<br/>
    Default: `3`
- **`FROM_AIRPORT`**: The IATA code of the airport you want to flight from. You can find the list on [nationsonline.org](https://www.nationsonline.org/oneworld/IATA_Codes/airport_code_list.htm).<br/>
    Example: `PAR`
- **`FROM_ALLOW_NEARBY_AIRPORTS`**: Accept other location nearby to the airport defined above.<br/>
    Default: `false`
- **`DESTINATION_AIRPORT`**: The IATA code of the airport you want to flight to.<br/>
    Example: `YUL`
- **`DESTINATION_ALLOW_NEARBY_AIRPORTS`**: Accept other location nearby to the defined destination airport.<br/>
    Default: `false`
- **`MIN_NIGHTS`**: How many nights you want to stay at least.<br/>
    Example: `14`
- **`MAX_NIGHTS`**: How many nights you want to stay at most.<br/>
    Example: `21`
- **`SEARCH_DATE_BEGIN`**: The first day to look for flights. Use `YYYY-MM-DD` format.<br/>
    Example: `2023-01-01`
- **`SEARCH_DATE_END`**: The last day to look for flights.<br/>
    Example: `2023-04-01`
- **`MAX_STOPS`**: The maximum number of layovers. 0 is equivalent to a non-stop (direct) flight.<br/>
    Choices: `0`, `1`, `2` (equivalent to "two or more")<br/>
    Default: `2`
- **`MAX_FLIGHT_DURATION`**: Maximum total flight duration, in hours. You can use floating values.<br/>
    Default: `240.0`
- **`MIN_LAYOVER_DURATION`**: Minimum layover duration (waiting time between two flights) in hours (float).<br/>
    Default: `0.0`
- **`MAX_LAYOVER_DURATION`**: Maximum layover duration (waiting time between two flights) in hours (float).<br/>
    Default: `72.0`
- **`PASSENGER_ADULTS`**: Number of non-student adult passengers, between 18 ans 65 years old.<br/>
    Default: `1`
- **`PASSENGER_STUDENTS`**: Students aged of more than 18 years old. A student certificate would be required.<br/>
    Default: `0`
- **`PASSENGER_SENIORS`**: More than 65 years old.<br/>
    Default: `0`
- **`PASSENGER_YOUTHS`**: Between 12 ans 17 years old.<br/>
    Default: `0`
- **`PASSENGER_CHILDREN`**: Between 2 and 11 years old..<br/>
    Default: `0`
- **`PASSENGER_TODDLERS_IN_OWN_SEAT`**: Less than 2 years old.<br/>
    Default: `0`
- **`PASSENGER_INFANTS_ON_LAP`**: Less than years old, but on your lap (How many infants per adult on his laps are authorized?)<br/>
    Default: `0`
- **`CARRY_ON_BAG_PER_PASSENGER`**: How many bags or suitcases per passenger (the little one that generally goes in cabin with you).<br/>
    Default: `1`
- **`CHECKED_BAG_PER_PASSENGER`**: How many checked bagage per passenger (the big one that generally goes in the hold).<br/>
    Default: `0`

### Examples

- Paris - Montreal on kayak.fr, between 6 to 12 nights:

```env
SEARCH_DATE_BEGIN=2023-01-01
SEARCH_DATE_END=2023-04-01

WEBSITE_URL="https://www.kayak.fr"
WEBSITE_LANGUAGE="fr"
NUMBER_OF_RESULTS=5

PASSENGER_ADULTS=1
CARRY_ON_BAG_PER_PASSENGER=1
CHECKED_BAG_PER_PASSENGER=0

MIN_NIGHTS=6
MAX_NIGHTS=12

MAX_STOPS=1

MAX_FLIGHT_DURATION=15
MAX_LAYOVER_DURATION=8

FROM_AIRPORT="CDG"
FROM_ALLOW_NEARBY_AIRPORTS=true

DESTINATION_AIRPORT="YUL"
DESTINATION_ALLOW_NEARBY_AIRPORTS=true
```

- New-York - Sydney on kayak.com, between 30 - 50 nights, with a long layover rallowed:

```env
SEARCH_DATE_BEGIN=2023-03-01
SEARCH_DATE_END=2023-05-01

WEBSITE_URL="https://www.kayak.com"
WEBSITE_LANGUAGE="en"
NUMBER_OF_RESULTS=3

PASSENGER_ADULTS=2
PASSENGER_CHILDREN=2
CARRY_ON_BAG_PER_PASSENGER=1
CHECKED_BAG_PER_PASSENGER=1

MIN_NIGHTS=30
MAX_NIGHTS=50

MAX_STOPS=1

MAX_FLIGHT_DURATION=120
MAX_LAYOVER_DURATION=96

FROM_AIRPORT="NYC"
FROM_ALLOW_NEARBY_AIRPORTS=false

DESTINATION_AIRPORT="SYD"
DESTINATION_ALLOW_NEARBY_AIRPORTS=true
```

## Development

This project uses Pre-commit. Make sure to install it.

```shell
> pre-commit install --hook-type pre-commit --hook-type pre-push
```

## Contributing

This project was written just for fun and could be easily broken by Kayak updates. However, if you find this project useful and you want to contribute, pull requests are very welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the terms of the [AGPL 3 license](./LICENSE).
