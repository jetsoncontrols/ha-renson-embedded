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
