# fff - the Flexible Flight Finder

Find the cheapest round-trip flight with more flexible dates than online flight comparators.

Round-trip search is done as following:

- Source and destination airports
- How many nights you want to stay (ex: between 12 and 15 nights)
- The date range you can potentially travel (ex: from January 2023 to August 2023)

You can also specify:

- Allow nearby airports
- How many stops at most (direct only, one stop, unlimited)
- Number of passengers (you can specify adults, seniors, students, children...)
- How many baggages per passenger (carry-on and checked)

# How to run

## Natively (Windows, MacOS, Linux)

Requirements:

- [Python 3.10](https://www.python.org/downloads/)
- [Geckodriver](https://github.com/mozilla/geckodriver/releases)
- [Mozilla Firefox](https://www.mozilla.org/firefox)

## With Docker

```shell
docker build -t fff .
docker run fff
```

# Configuration

The configuration is located at `fff/config.py`.
You can override any of the settings with a `.env` file at the project root directory (or just pass the environment variables to Docker if you're using it).
