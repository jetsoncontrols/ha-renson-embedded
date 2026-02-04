"""Test fixtures for Renson Embedded integration."""
import json
from pathlib import Path

import pytest


@pytest.fixture
def test_config():
    """Load test configuration from config file."""
    config_path = Path(__file__).parent / "test_config.json"

    if not config_path.exists():
        pytest.skip("test_config.json not found. Create it to run integration tests.")

    with open(config_path) as f:
        config = json.load(f)

    required_keys = ["host"]
    missing_keys = [key for key in required_keys if key not in config]

    if missing_keys:
        pytest.skip(f"Missing required config keys: {missing_keys}")

    return config


@pytest.fixture
def renson_host(test_config):
    """Get the Renson device host from test config."""
    return test_config["host"]


@pytest.fixture
def renson_user_type(test_config):
    """Get the Renson device user type from test config.

    Valid types: 'User', 'Professional', 'Renson Technician'
    """
    return test_config.get("user_type", "User")


@pytest.fixture
def renson_password(test_config):
    """Get the Renson device password from test config (if required)."""
    return test_config.get("password")
