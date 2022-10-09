#!/usr/bin/env python3


from fff.bot import Bot
from fff.utils.logging import logger


def main():
    with logger.catch():
        bot = Bot()
        bot.start()


if __name__ == "__main__":
    main()
