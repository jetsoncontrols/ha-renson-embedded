"""Client for communicating with Renson Embedded device."""
from __future__ import annotations

import asyncio
import ssl
from typing import Any

import aiohttp


class RensonClient:
    """Client to communicate with Renson Embedded device via REST API."""

    def __init__(self, host: str, user_type: str = "user", password: str | None = None) -> None:
        """Initialize the client.

        Args:
            host: The IP address or hostname of the Renson device
            user_type: User type for authentication ('user', 'professional', or 'renson technician')
            password: Password for authentication (if required)
        """
        self.host = host
        self.base_url = f"https://{host}"
        self.user_type = user_type.lower()
        self.password = password
        self._token: str | None = None
        self._session: aiohttp.ClientSession | None = None

        # Create SSL context that ignores self-signed certificates
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE

    async def async_login(self) -> str:
        """Authenticate with the Renson device and get a JWT token.

        Returns:
            JWT token string

        Raises:
            aiohttp.ClientError: If authentication fails
        """
        if not self._session:
            self._session = aiohttp.ClientSession()

        url = f"{self.base_url}/api/v1/authenticate"
        payload = {
            "user_name": self.user_type,
            "user_pwd": self.password
        }

        async with self._session.post(url, json=payload, ssl=self._ssl_context) as response:
            response.raise_for_status()
            data = await response.json()

            if "token" not in data:
                raise ValueError("No token received from authentication")

            self._token = data["token"]
            return self._token

    async def async_logout(self) -> None:
        """Logout from the Renson device.

        Note: The Renson device may not have a logout endpoint.
        JWT tokens are likely handled client-side only.
        This method attempts logout but does not fail if unsuccessful.
        """
        if not self._token or not self._session:
            return

        try:
            url = f"{self.base_url}/api/v1/logout"
            headers = {"Authorization": f"Bearer {self._token}"}
            async with self._session.post(url, headers=headers, ssl=self._ssl_context) as response:
                # Don't raise on failure - logout endpoint may not exist
                pass
        except Exception:
            # Silently handle logout failures
            pass
        finally:
            self._token = None

    async def async_close(self) -> None:
        """Close the client session and logout."""
        await self.async_logout()
        if self._session:
            await self._session.close()
            self._session = None

    def _get_headers(self) -> dict[str, str]:
        """Get headers with authentication token."""
        if not self._token:
            raise ValueError("Not authenticated. Call async_login() first.")
        return {"Authorization": f"Bearer {self._token}"}

    async def async_get_status(self) -> dict[str, Any]:
        """Get the current status of the device."""
        # TODO: Implement REST API call to get status
        pass

    async def async_open_roof(self) -> None:
        """Open the pergola roof."""
        # TODO: Implement REST API call to open
        pass

    async def async_close_roof(self) -> None:
        """Close the pergola roof."""
        # TODO: Implement REST API call to close
        pass

    async def async_stop_roof(self) -> None:
        """Stop the pergola roof."""
        # TODO: Implement REST API call to stop
        pass

    async def async_set_roof_position(self, position: int) -> None:
        """Set the pergola roof to a specific position."""
        # TODO: Implement REST API call to set position
        pass
