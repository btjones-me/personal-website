"""Smoke test for absolute imports."""


def test_absolute_imports_work():
    """Test that all modules can be imported using absolute imports."""
    # These should not raise ImportError
    from personal_website import __version__
    from personal_website.config import config
    from personal_website.logger import logger
    
    # Basic assertions to ensure imports worked
    assert __version__ is not None
    assert config is not None
    assert logger is not None


def test_dashboard_imports():
    """Test that dashboard module imports work."""
    # This should not raise ImportError
    import personal_website.dashboard
    
    assert personal_website.dashboard is not None
