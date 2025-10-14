"""Configuration management."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


config = Config()
