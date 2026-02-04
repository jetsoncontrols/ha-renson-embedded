"""Test fixtures for Renson Embedded integration."""
import asyncio
import json
import ssl
from pathlib import Path

import aiohttp
import pytest


@pytest.fixture(scope="session")
def test_config():
    """Load test configuration from config file.

    Session-scoped to allow session-scoped authenticated_client fixture.
    """
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


@pytest.fixture(scope="session")
def renson_host(test_config):
    """Get the Renson device host from test config."""
    return test_config["host"]


@pytest.fixture(scope="session")
def renson_user_type(test_config):
    """Get the Renson device user type from test config.

    Valid types: 'User', 'Professional', 'Renson Technician'
    """
    return test_config.get("user_type", "User")


@pytest.fixture(scope="session")
def renson_password(test_config):
    """Get the Renson device password from test config (if required)."""
    return test_config.get("password")


@pytest.fixture
def ssl_context():
    """Create SSL context that ignores self-signed certificates."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


@pytest.fixture(scope="function")
def rate_limit_delay():
    """Add delay after tests to avoid rate limiting on lifecycle tests.

    The Renson device rate limits authentication requests.
    This fixture is only needed for TestRensonClientLifecycle tests
    that create their own client instances.
    """
    yield
    # Delay after test completes to avoid rate limiting
    import time
    time.sleep(2)


@pytest.fixture(scope="function")
async def authenticated_client(test_config):
    """Provide a function-scoped authenticated RensonClient.

    This fixture:
    1. Creates a client instance with RensonConfig
    2. Authenticates at the start of each test
    3. Yields the client for the test to use
    4. Logs out and closes the session at the end

    Note: Changed from session to function scope due to aiohttp event loop limitations.
    """
    # Import here to avoid circular imports
    import importlib.util
    from pathlib import Path

    config_path = Path(__file__).parent.parent / "custom_components" / "renson_embedded" / "api" / "config.py"
    spec = importlib.util.spec_from_file_location("renson_config", config_path)
    renson_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renson_config)
    RensonConfig = renson_config.RensonConfig

    client_path = Path(__file__).parent.parent / "custom_components" / "renson_embedded" / "api" / "client.py"
    spec = importlib.util.spec_from_file_location("renson_client", client_path)
    renson_client = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renson_client)
    RensonClient = renson_client.RensonClient

    # Create config and client
    config = RensonConfig(
        host=test_config["host"],
        user_type=test_config.get("user_type", "User"),
        password=test_config.get("password")
    )
    client = RensonClient(config)

    await client.async_login()

    yield client

    # Cleanup: logout and close
    await client.async_close()
