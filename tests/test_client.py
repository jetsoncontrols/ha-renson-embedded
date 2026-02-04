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
    async def test_login(self, renson_host, renson_user_type, renson_password):
        """Test logging into the Renson web interface using the client.

        Endpoint: POST /api/v1/authenticate
        Payload: {"user_name": "user", "user_pwd": "password"}
        Response: {"user_role": "USER", "token": "JWT_TOKEN"}
        """
        client = RensonClient(renson_host, renson_user_type, renson_password)

        try:
            print(f"\n=== Testing Authentication with RensonClient ===")
            print(f"Host: {renson_host}")
            print(f"User Type: {renson_user_type}")

            token = await client.async_login()

            print(f"✓ LOGIN SUCCESSFUL")
            print(f"  Token: {token[:50]}...")

            # Verify we got a valid token
            assert token, "Token is empty"
            assert isinstance(token, str), "Token should be a string"

            return token
        finally:
            await client.async_close()

    @pytest.mark.asyncio
    async def test_logout(self, renson_host, renson_user_type, renson_password):
        """Test logout functionality using the client.

        The client should handle logout gracefully even if no logout endpoint exists.
        """
        client = RensonClient(renson_host, renson_user_type, renson_password)

        try:
            print(f"\n=== Testing Logout with RensonClient ===")

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
    async def test_client_context_manager(self, renson_host, renson_user_type, renson_password):
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

    @pytest.mark.asyncio
    async def test_authenticated_session_fixture(self, authenticated_session):
        """Test that authenticated_session fixture provides a working session with token."""
        session = authenticated_session

        # Verify session has expected attributes
        assert hasattr(session, 'renson_token'), "Session missing renson_token attribute"
        assert hasattr(session, 'renson_base_url'), "Session missing renson_base_url attribute"
        assert hasattr(session, 'renson_ssl_context'), "Session missing renson_ssl_context attribute"

        assert session.renson_token, "Token is empty"
        assert session.renson_base_url.startswith('https://'), "Base URL should use HTTPS"

        print(f"\n✓ Authenticated session fixture working")
        print(f"  Base URL: {session.renson_base_url}")
        print(f"  Token: {session.renson_token[:50]}...")

    @pytest.mark.asyncio
    async def test_get_status(self, renson_host, renson_user_type, renson_password):
        """Test getting device status."""
        # TODO: Implement test
        pass

    @pytest.mark.asyncio
    async def test_open(self, renson_host, renson_user_type, renson_password):
        """Test opening the pergola roof."""
        # TODO: Implement test
        pass

    @pytest.mark.asyncio
    async def test_close(self, renson_host, renson_user_type, renson_password):
        """Test closing the pergola roof."""
        # TODO: Implement test
        pass

    @pytest.mark.asyncio
    async def test_stop(self, renson_host, renson_user_type, renson_password):
        """Test stopping the pergola roof."""
        # TODO: Implement test
        pass

    @pytest.mark.asyncio
    async def test_set_position(self, renson_host, renson_user_type, renson_password):
        """Test setting pergola roof position."""
        # TODO: Implement test
        pass
