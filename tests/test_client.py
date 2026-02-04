"""Tests for Renson client."""
import importlib.util
import sys
from pathlib import Path

import pytest

# Import config.py first, then client.py from api subfolder
config_path = Path(__file__).parent.parent / "custom_components" / "renson_embedded" / "api" / "config.py"
spec = importlib.util.spec_from_file_location("renson_config", config_path)
renson_config = importlib.util.module_from_spec(spec)
sys.modules["renson_config"] = renson_config
spec.loader.exec_module(renson_config)
RensonConfig = renson_config.RensonConfig

client_path = Path(__file__).parent.parent / "custom_components" / "renson_embedded" / "api" / "client.py"
spec = importlib.util.spec_from_file_location("renson_client", client_path)
renson_client = importlib.util.module_from_spec(spec)
sys.modules["renson_client"] = renson_client
spec.loader.exec_module(renson_client)
RensonClient = renson_client.RensonClient


class TestRensonClient:
    """Tests for RensonClient."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, renson_host):
        """Test that client can be initialized with config."""
        config = RensonConfig(host=renson_host, user_type="user", password="password")
        client = RensonClient(config)

        assert client.host == renson_host
        assert client.base_url == f"https://{renson_host}"
        assert client.config.user_type == "user"
        assert client.config.password == "password"
        assert client.config.verify_ssl is False  # Default
        assert client.config.timeout == 30  # Default

    @pytest.mark.asyncio
    async def test_authenticated_client_has_token(self, authenticated_client):
        """Test that the shared authenticated client has a valid token."""
        print(f"\n=== Testing Authenticated Client ===")
        print(f"Host: {authenticated_client.host}")
        print(f"Token: {authenticated_client._token[:50]}...")

        assert authenticated_client._token, "Client should have a token"
        assert isinstance(authenticated_client._token, str), "Token should be a string"
        assert authenticated_client._session is not None, "Client should have an active session"

        print(f"✓ Authenticated client is ready")

    @pytest.mark.asyncio
    async def test_get_status(self, authenticated_client):
        """Test getting device status using authenticated client.

        The API endpoint /api/v1/skye2/roof/status returns:
        - state: Overall device state (ready, moving, homing, error, etc.)
        - current_roof_positions: Contains stack and tilt positions
          - stack: Stack position as percentage (0-100)
          - tilt: Tilt/rotation position in degrees (0-90)
        - locked: Whether the roof is locked
        - p1_status/p2_status: Detailed motor controller status
        - action_status: Current action state and completion
        """
        # Verify client is authenticated before calling
        assert authenticated_client._token, "Client must be authenticated"

        print(f"\n=== Testing Get Status ===")
        print(f"Endpoint: {authenticated_client.base_url}{authenticated_client.config.path}")

        status = await authenticated_client.async_get_status()

        print(f"✓ STATUS RETRIEVED")

        # Verify we got a response
        assert status is not None, "Status should not be None"
        assert isinstance(status, dict), "Status should be a dictionary"

        # Verify required top-level fields exist
        assert "state" in status, "Response should contain 'state'"
        assert "current_roof_positions" in status, "Response should contain 'current_roof_positions'"
        assert "locked" in status, "Response should contain 'locked'"

        # Verify roof positions structure
        positions = status["current_roof_positions"]
        assert "stack" in positions, "Positions should contain 'stack'"
        assert "tilt" in positions, "Positions should contain 'tilt'"

        # Log discovered values
        print(f"  State: {status['state']}")
        print(f"  Locked: {status['locked']}")
        print(f"  Stack Position: {positions['stack']:.2f}%")
        print(f"  Tilt Position: {positions['tilt']:.2f}°")

        # Verify data types
        assert isinstance(status["state"], str), "State should be a string"
        assert isinstance(status["locked"], bool), "Locked should be a boolean"
        assert isinstance(positions["stack"], (int, float)), "Stack should be numeric"
        assert isinstance(positions["tilt"], (int, float)), "Tilt should be numeric"

        print(f"  ✓ All expected fields present and valid")

    @pytest.mark.asyncio
    async def test_open(self, authenticated_client):
        """Test opening the pergola roof using authenticated client."""
        # Verify client is authenticated before calling
        assert authenticated_client._token, "Client must be authenticated"

        # TODO: Implement once we discover the open endpoint
        pass

    @pytest.mark.asyncio
    async def test_close(self, authenticated_client):
        """Test closing the pergola roof using authenticated client."""
        # Verify client is authenticated before calling
        assert authenticated_client._token, "Client must be authenticated"

        # TODO: Implement once we discover the close endpoint
        pass

    @pytest.mark.asyncio
    async def test_stop(self, authenticated_client):
        """Test stopping the pergola roof using authenticated client."""
        # Verify client is authenticated before calling
        assert authenticated_client._token, "Client must be authenticated"

        # TODO: Implement once we discover the stop endpoint
        pass

    @pytest.mark.asyncio
    async def test_set_position(self, authenticated_client):
        """Test setting pergola roof position using authenticated client."""
        # Verify client is authenticated before calling
        assert authenticated_client._token, "Client must be authenticated"

        # TODO: Implement once we discover the set position endpoint
        pass


class TestRensonClientLifecycle:
    """Tests for RensonClient authentication lifecycle.

    These tests need their own client instances to test login/logout behavior.
    """

    @pytest.mark.asyncio
    async def test_login(self, renson_host, renson_user_type, renson_password, rate_limit_delay):
        """Test logging into the Renson web interface using the client.

        Endpoint: POST /api/v1/authenticate
        Payload: {"user_name": "user", "user_pwd": "password"}
        Response: {"user_role": "USER", "token": "JWT_TOKEN"}
        """
        config = RensonConfig(
            host=renson_host,
            user_type=renson_user_type,
            password=renson_password
        )
        client = RensonClient(config)

        try:
            print(f"\n=== Testing Login ===")
            print(f"Host: {renson_host}")
            print(f"User Type: {renson_user_type}")

            token = await client.async_login()

            print(f"✓ LOGIN SUCCESSFUL")
            print(f"  Token: {token[:50]}...")

            # Verify we got a valid token
            assert token, "Token is empty"
            assert isinstance(token, str), "Token should be a string"
            assert client._session is not None, "Session should be created"
        finally:
            await client.async_close()

    @pytest.mark.asyncio
    async def test_logout(self, renson_host, renson_user_type, renson_password, rate_limit_delay):
        """Test logout functionality using the client.

        The client should handle logout gracefully even if no logout endpoint exists.
        """
        config = RensonConfig(
            host=renson_host,
            user_type=renson_user_type,
            password=renson_password
        )
        client = RensonClient(config)

        try:
            print(f"\n=== Testing Logout ===")

            # Login first
            token = await client.async_login()
            print(f"Logged in with token: {token[:50]}...")

            # Logout
            await client.async_logout()
            print(f"✓ LOGOUT COMPLETED")

            # Verify token is cleared
            assert client._token is None, "Token should be cleared after logout"
        finally:
            await client.async_close()

    @pytest.mark.asyncio
    async def test_client_context_manager(self, renson_host, renson_user_type, renson_password, rate_limit_delay):
        """Test that client properly manages session lifecycle."""
        config = RensonConfig(
            host=renson_host,
            user_type=renson_user_type,
            password=renson_password
        )
        client = RensonClient(config)

        # Login
        token = await client.async_login()
        assert token, "Should have token after login"
        assert client._session is not None, "Session should be created"

        # Close
        await client.async_close()
        assert client._token is None, "Token should be cleared"
        assert client._session is None, "Session should be closed"
