"""Configuration management."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # LLM Configuration
    PYDANTIC_AI_GATEWAY_API_KEY = os.getenv("PYDANTIC_AI_GATEWAY_API_KEY", "")
    _LLM_MODEL_ENV = os.getenv("LLM_MODEL")
    LLM_MODEL = _LLM_MODEL_ENV or "gateway/google-vertex:gemini-2.5-flash"
    LLM_MAX_INPUT_CHARS = int(os.getenv("LLM_MAX_INPUT_CHARS", "500"))
    LLM_MAX_CONVERSATION_TURNS = int(os.getenv("LLM_MAX_CONVERSATION_TURNS", "10"))
    LLM_RATE_LIMIT_PER_MINUTE = int(os.getenv("LLM_RATE_LIMIT_PER_MINUTE", "10"))


config = Config()
