"""Logging configuration."""

from loguru import logger

from personal_website.config import config

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level=config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
)

if config.DEBUG:
    logger.add(
        lambda msg: print(msg, end=""),
        level=config.LOG_LEVEL,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
    )
