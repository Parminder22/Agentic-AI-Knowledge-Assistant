import sys
from loguru import logger


def setup_logger(debug: bool = False):
    logger.remove()  # Remove default handler

    level = "DEBUG" if debug else "INFO"

    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    logger.add(
        "logs/app.log",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    return logger
