"""Test configuration module."""

from personal_website.config import Config, config


def test_config_class_exists():
    """Test Config class can be instantiated."""
    test_config = Config()
    assert hasattr(test_config, "DEBUG")
    assert hasattr(test_config, "LOG_LEVEL")


def test_config_instance_exists():
    """Test config instance is available."""
    assert hasattr(config, "DEBUG")
    assert hasattr(config, "LOG_LEVEL")
    assert isinstance(config.DEBUG, bool)
    assert isinstance(config.LOG_LEVEL, str)


def test_config_values_are_reasonable():
    """Test config values are reasonable."""
    assert config.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
