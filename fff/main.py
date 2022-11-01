#!/usr/bin/env python3


from fff.bot import Bot
from fff.utils.logging import logger


def main():
    with logger.catch():
        print(
            "Starting the bot. The scraping will take several minutes depending on your configuration."
        )
        bot = Bot()
        bot.search()


if __name__ == "__main__":
    main()
