import logging

from loguru import logger as loguru_logger


class InterceptHandler(logging.Handler):  # type: ignore
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Uncomment this line to redirect all the log to loguru
# logging.basicConfig(handlers=[InterceptHandler()], level=0)

# Use this object in user code
logger = loguru_logger
