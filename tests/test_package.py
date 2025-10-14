"""Test package imports and version."""

import personal_website


def test_package_has_version():
    """Test package has version attribute."""
    assert hasattr(personal_website, "__version__")
    assert isinstance(personal_website.__version__, str)


def test_version_format():
    """Test version follows semantic versioning."""
    version = personal_website.__version__
    parts = version.split(".")
    assert len(parts) >= 2  # At least major.minor
    assert all(part.isdigit() for part in parts[:2])  # Major and minor are numeric
