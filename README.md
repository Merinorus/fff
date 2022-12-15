# fff - the Flexible Flight Finder

Find the cheapest round-trip flight with more flexible dates than online flight comparators.

## Features

FFF is a command-line interface to help scraping Kayak's round trips with the [flexible date](https://www.kayak.com/news/flexible-dates-nearby-airports/) mode only.

A round-trip search on Kayak is done as following:

- Specify **source** and **destination** airports
- **How many nights** you want to stay (eg: between 12 and 15 nights)
- The **travel period** (eg: January 2023)

But there are some limitations on Kayak:

- You cannot specify an interval duration higher that 7 days (eg: you cannot search a trip between 10 and 20 days)
- The search period is limited to 4 weeks (eg: you cannot look for a flight from january to mars)

**This tool removes these limits.**

## How to run

### Natively (Windows, MacOS, Linux)

Requirements:

- [Python 3.10](https://www.python.org/downloads/)
- [Geckodriver](https://github.com/mozilla/geckodriver/releases)
- [Mozilla Firefox](https://www.mozilla.org/firefox)

### With Docker

```shell
docker-compose up --build
```

## Configuration

The configuration is located at `fff/config.py`.
You can override any of the settings with a `.env` file at the project root directory (or just pass the environment variables to Docker if you're using it).

An `example.env` file is available to help you writing your own trip.

## Development

```shell
pre-commit install --hook-type pre-commit --hook-type pre-push
```
