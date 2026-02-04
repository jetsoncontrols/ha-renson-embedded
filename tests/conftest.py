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


@pytest.fixture(scope="session")
async def authenticated_client(test_config):
    """Provide a session-scoped authenticated RensonClient.

    This fixture:
    1. Creates a single client instance
    2. Authenticates once at the start of the test session
    3. Yields the client for all tests to use
    4. Logs out and closes the session at the end

    This matches real-world usage: log in once, do multiple operations, log out when done.
    """
    # Import here to avoid circular imports
    import importlib.util
    from pathlib import Path

    client_path = Path(__file__).parent.parent / "custom_components" / "renson_embedded" / "client.py"
    spec = importlib.util.spec_from_file_location("renson_client", client_path)
    renson_client = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renson_client)
    RensonClient = renson_client.RensonClient

    # Create and login
    client = RensonClient(
        test_config["host"],
        test_config.get("user_type", "User"),
        test_config.get("password")
    )

    print(f"\n=== Session Setup: Authenticating to {test_config['host']} ===")
    await client.async_login()
    print(f"✓ Session authenticated successfully")

    yield client

    # Cleanup: logout and close
    print(f"\n=== Session Teardown: Logging out ===")
    await client.async_close()
    print(f"✓ Session closed")
