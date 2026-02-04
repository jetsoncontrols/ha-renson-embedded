"""Test fixtures for Renson Embedded integration."""
import asyncio
import json
import ssl
from pathlib import Path

import aiohttp
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


@pytest.fixture
def ssl_context():
    """Create SSL context that ignores self-signed certificates."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


@pytest.fixture(scope="function")
def rate_limit_delay():
    """Add delay between tests to avoid rate limiting.

    The Renson device rate limits authentication requests.
    This fixture adds a 2 second delay after tests that authenticate.
    """
    yield
    # Delay after test completes to avoid rate limiting
    import time
    time.sleep(2)


@pytest.fixture
async def authenticated_session(renson_host, renson_user_type, renson_password, ssl_context, rate_limit_delay):
    """Provide an authenticated aiohttp session with automatic logout cleanup.

    This fixture:
    1. Creates a session
    2. Authenticates and gets a token
    3. Yields the session with the token
    4. Logs out after the test completes
    """
    async with aiohttp.ClientSession() as session:
        base_url = f"https://{renson_host}"

        # Login
        login_url = f"{base_url}/api/v1/authenticate"
        user_name = renson_user_type.lower()
        payload = {
            "user_name": user_name,
            "user_pwd": renson_password
        }

        async with session.post(login_url, json=payload, ssl=ssl_context) as response:
            if response.status != 200:
                pytest.fail(f"Login failed with status {response.status}")

            data = await response.json()
            token = data.get("token")

            if not token:
                pytest.fail("No token received from authentication")

        # Store token and base URL for convenience
        session.renson_token = token
        session.renson_base_url = base_url
        session.renson_ssl_context = ssl_context

        # Yield session to test
        yield session

        # Logout after test completes
        try:
            logout_url = f"{base_url}/api/v1/logout"
            headers = {"Authorization": f"Bearer {token}"}
            async with session.post(logout_url, headers=headers, ssl=ssl_context) as response:
                # Don't fail test if logout fails, just log it
                if response.status not in [200, 401, 404]:
                    print(f"\nWarning: Logout returned status {response.status}")
        except Exception as e:
            print(f"\nWarning: Logout failed with error: {e}")
