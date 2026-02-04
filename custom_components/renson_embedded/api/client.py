"""Client for communicating with Renson Embedded device."""
from __future__ import annotations

import asyncio
import ssl
import sys
from typing import Any

import aiohttp

try:
    from .config import RensonConfig
except ImportError:
    # Handle direct module imports (e.g., in tests)
    from renson_config import RensonConfig


class RensonClient:
    """Client to communicate with Renson Embedded device via REST API."""

    def __init__(self, config: RensonConfig) -> None:
        """Initialize the client.

        Args:
            config: RensonConfig instance with all configuration options
        """
        self.config = config
        self._token: str | None = None
        self._session: aiohttp.ClientSession | None = None

        # Create SSL context based on config
        self._ssl_context = ssl.create_default_context()
        if not config.verify_ssl:
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE

    @property
    def host(self) -> str:
        """Get the host from config."""
        return self.config.host

    @property
    def base_url(self) -> str:
        """Get the base URL from config."""
        return self.config.base_url

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
            "user_name": self.config.user_type,
            "user_pwd": self.config.password
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
        """Get the current status of the device.

        Returns:
            Dictionary containing:
            - state: Current state of the device
            - slide_position: Slide position (if applicable)
            - rotation_position: Rotation position (if applicable)

        Raises:
            ValueError: If not authenticated
            aiohttp.ClientError: If request fails
        """
        if not self._session:
            raise ValueError("Not authenticated. Call async_login() first.")

        url = f"{self.base_url}{self.config.path}"
        headers = self._get_headers()

        async with self._session.get(url, headers=headers, ssl=self._ssl_context) as response:
            response.raise_for_status()

            # Check content type to see if we're getting JSON or HTML
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                data = await response.json()
                return data
            else:
                # Return text for debugging
                text = await response.text()
                return {"_content_type": content_type, "_preview": text[:500]}

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
