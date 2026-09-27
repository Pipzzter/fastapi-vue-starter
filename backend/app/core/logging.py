"""Route the standard library ``logging`` module through Loguru.

Uses the canonical Loguru ``InterceptHandler`` so that logs emitted by the app,
Uvicorn, and third-party libraries all flow through a single sink with a
consistent format and the correct level/traceback preserved.
"""

import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(level: int = logging.INFO) -> None:
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(level)

    for name in list(logging.root.manager.loggerDict):
        std_logger = logging.getLogger(name)
        std_logger.handlers = []
        std_logger.propagate = True

    logger.remove()
    logger.add(sys.stdout, level=level, backtrace=False, diagnose=False)
