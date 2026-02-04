"""Tests for Renson client."""
import importlib.util
import ssl
import sys
from pathlib import Path

import aiohttp
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
        client = RensonClient(renson_host)
        assert client.host == renson_host
        assert client.base_url == f"http://{renson_host}"

    @pytest.mark.asyncio
    async def test_login(self, renson_host, renson_user_type, renson_password):
        """Test logging into the Renson web interface.

        Endpoint: POST /api/v1/authenticate
        Payload: {"user_name": "user", "user_pwd": "password"}
        Response: {"user_role": "USER", "token": "JWT_TOKEN"}
        """
        # Create SSL context that ignores self-signed certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with aiohttp.ClientSession() as session:
            base_url = f"https://{renson_host}"
            url = f"{base_url}/api/v1/authenticate"

            # Build payload - user_type needs to be converted to lowercase "user" format
            user_name = renson_user_type.lower()
            payload = {
                "user_name": user_name,
                "user_pwd": renson_password
            }

            print(f"\n=== Testing Authentication ===")
            print(f"URL: {url}")
            print(f"Payload: {payload}")

            async with session.post(url, json=payload, ssl=ssl_context) as response:
                print(f"Status: {response.status}")

                assert response.status == 200, f"Login failed with status {response.status}"

                data = await response.json()
                print(f"Response: {data}")

                # Verify we got a token
                assert "token" in data, "Response missing token field"
                assert data["token"], "Token is empty"

                # Verify user role
                assert "user_role" in data, "Response missing user_role field"

                print(f"✓ LOGIN SUCCESSFUL")
                print(f"  User Role: {data['user_role']}")
                print(f"  Token: {data['token'][:50]}...")

                return data["token"]

    @pytest.mark.asyncio
    async def test_logout(self, renson_host, renson_user_type, renson_password):
        """Test logout functionality.

        First authenticate, then try to discover and test the logout endpoint.
        """
        # Create SSL context that ignores self-signed certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with aiohttp.ClientSession() as session:
            base_url = f"https://{renson_host}"

            # First, login to get a token
            login_url = f"{base_url}/api/v1/authenticate"
            user_name = renson_user_type.lower()
            payload = {
                "user_name": user_name,
                "user_pwd": renson_password
            }

            async with session.post(login_url, json=payload, ssl=ssl_context) as response:
                assert response.status == 200, f"Login failed with status {response.status}"
                data = await response.json()
                token = data["token"]

            print(f"\n=== Testing Logout Endpoints ===")
            print(f"Token: {token[:50]}...")

            # Try common logout endpoints
            logout_endpoints = [
                "/api/v1/logout",
                "/api/v1/auth/logout",
                "/api/logout",
                "/logout",
                "/api/v1/session",
            ]

            headers = {"Authorization": f"Bearer {token}"}

            for endpoint in logout_endpoints:
                url = f"{base_url}{endpoint}"
                print(f"\nTesting: {url}")

                # Try POST
                try:
                    async with session.post(url, headers=headers, ssl=ssl_context) as response:
                        print(f"  POST status: {response.status}")
                        if response.status == 200:
                            print(f"  ✓ LOGOUT SUCCESSFUL (POST)")
                            return
                        if response.status not in [404, 405]:
                            text = await response.text()
                            print(f"  Response: {text[:200]}")
                except Exception as e:
                    print(f"  POST error: {e}")

                # Try DELETE
                try:
                    async with session.delete(url, headers=headers, ssl=ssl_context) as response:
                        print(f"  DELETE status: {response.status}")
                        if response.status == 200:
                            print(f"  ✓ LOGOUT SUCCESSFUL (DELETE)")
                            return
                        if response.status not in [404, 405]:
                            text = await response.text()
                            print(f"  Response: {text[:200]}")
                except Exception as e:
                    print(f"  DELETE error: {e}")

            print("\n=== Logout endpoint discovery needed ===")
            print("Please check browser dev tools for the logout API call")

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
