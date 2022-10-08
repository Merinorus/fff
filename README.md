# fff - the flexible flight finder

Find the cheapest flight with more flexible dates than online flight comparators.

Search is done as following:

- How many nights for your travel (ex: between 9 and 15 nights)
- A date range (ex: between 1/01/2023 and 1/05/2023)

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
