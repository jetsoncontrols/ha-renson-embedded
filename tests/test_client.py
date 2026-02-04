"""Tests for Renson client."""
import importlib.util
import sys
from pathlib import Path

import pytest

# Import client.py directly without triggering __init__.py
client_path = Path(__file__).parent.parent / "custom_components" / "renson_embedded" / "client.py"
spec = importlib.util.spec_from_file_location("renson_client", client_path)
renson_client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renson_client)
RensonClient = renson_client.RensonClient


class TestRensonClient:
    """Tests for RensonClient."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, renson_host):
        """Test that client can be initialized."""
        client = RensonClient(renson_host, "user", "password")
        assert client.host == renson_host
        assert client.base_url == f"https://{renson_host}"
        assert client.user_type == "user"
        assert client.password == "password"

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
        """Test getting device status using authenticated client."""
        # Verify client is authenticated before calling
        assert authenticated_client._token, "Client must be authenticated"

        # TODO: Implement once we discover the status endpoint
        pass

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
        client = RensonClient(renson_host, renson_user_type, renson_password)

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
        client = RensonClient(renson_host, renson_user_type, renson_password)

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
        client = RensonClient(renson_host, renson_user_type, renson_password)

        # Login
        token = await client.async_login()
        assert token, "Should have token after login"
        assert client._session is not None, "Session should be created"

        # Close
        await client.async_close()
        assert client._token is None, "Token should be cleared"
        assert client._session is None, "Session should be closed"
