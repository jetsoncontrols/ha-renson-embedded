"""Client for communicating with Renson Embedded device."""
from __future__ import annotations

import asyncio
import json
import logging
import ssl
from collections.abc import Callable
from typing import Any

import aiohttp

try:
    from .config import RensonConfig
except ImportError:
    # Handle direct module imports (e.g., in tests)
    from renson_config import RensonConfig

_LOGGER = logging.getLogger(__name__)


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
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._ws_task: asyncio.Task | None = None

        # Create SSL context based on config
        if not config.verify_ssl:
            self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE
        else:
            # Defer default context creation to avoid blocking the event loop
            self._ssl_context: ssl.SSLContext | None = None

    @property
    def host(self) -> str:
        """Get the host from config."""
        return self.config.host

    @property
    def base_url(self) -> str:
        """Get the base URL from config."""
        return self.config.base_url

    @property
    def ws_connected(self) -> bool:
        """Return True if WebSocket is connected."""
        return self._ws is not None and not self._ws.closed

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
        """Close the client session, disconnect WebSocket, and logout."""
        await self.async_disconnect_websocket()
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

    _WS_SUBSCRIPTIONS = [
        "ROOF_STATUS_CHANGED",
        "SKYE2_STATUS_CHANGED",
        "ROOF_SELF_TEST_STATUS_CHANGED",
        "DIGITAL_INPUT_STATUS_CHANGED",
        "SYSTEM_STATUS_CHANGED",
    ]
    _WS_PING_INTERVAL = 25  # seconds

    async def async_listen_websocket(
        self, callback: Callable[[dict[str, Any]], None]
    ) -> None:
        """Connect to the WebSocket and listen for events.

        Sends Authenticate and Subscribe messages after connecting,
        then maintains the connection with periodic pings.

        Args:
            callback: Called with parsed event data on each state change.
        """
        if not self._session or not self._token:
            raise ValueError("Not authenticated. Call async_login() first.")

        ws_base = self.base_url.replace("https://", "wss://").replace("http://", "ws://")
        url = f"{ws_base}/api/v1/ws/events"

        _LOGGER.debug("Connecting to WebSocket at %s", url)

        ping_task: asyncio.Task | None = None
        try:
            self._ws = await self._session.ws_connect(
                url, ssl=self._ssl_context
            )
            _LOGGER.debug("WebSocket connected")

            # Authenticate
            await self._ws.send_json({
                "type": "Authenticate",
                "data": {"bearer": self._token},
            })

            # Subscribe to events
            await self._ws.send_json({
                "type": "Subscribe",
                "data": {"subscriptions": self._WS_SUBSCRIPTIONS},
            })

            # Start ping loop
            ping_task = asyncio.create_task(self._ws_ping_loop())

            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    parsed = self._parse_ws_message(msg.data)
                    if parsed is not None:
                        callback(parsed)
                elif msg.type == aiohttp.WSMsgType.BINARY:
                    _LOGGER.debug(
                        "WebSocket binary message (%d bytes): %s",
                        len(msg.data),
                        msg.data[:500],
                    )
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    _LOGGER.error("WebSocket error: %s", self._ws.exception())
                    break
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSING,
                    aiohttp.WSMsgType.CLOSED,
                ):
                    _LOGGER.debug("WebSocket closed")
                    break
        except asyncio.CancelledError:
            _LOGGER.debug("WebSocket listener cancelled")
            raise
        except Exception:
            _LOGGER.exception("WebSocket connection error")
        finally:
            if ping_task and not ping_task.done():
                ping_task.cancel()
                try:
                    await ping_task
                except asyncio.CancelledError:
                    pass
            if self._ws and not self._ws.closed:
                await self._ws.close()
            self._ws = None

    async def _ws_ping_loop(self) -> None:
        """Send periodic ping messages to keep the WebSocket alive."""
        try:
            while self._ws and not self._ws.closed:
                await asyncio.sleep(self._WS_PING_INTERVAL)
                if self._ws and not self._ws.closed:
                    await self._ws.send_json({"type": "Ping", "data": {}})
        except asyncio.CancelledError:
            raise
        except Exception:
            _LOGGER.debug("WebSocket ping loop ended")

    # Protocol message types that are not state events
    _WS_PROTOCOL_TYPES = {"Authenticated", "SubscriptionsUpdated", "Ping", "Pong"}

    # Event types that carry state data
    _WS_EVENT_TYPES = {
        "ROOF_STATUS_CHANGED",
        "SKYE2_STATUS_CHANGED",
        "ROOF_SELF_TEST_STATUS_CHANGED",
        "DIGITAL_INPUT_STATUS_CHANGED",
        "SYSTEM_STATUS_CHANGED",
    }

    def _parse_ws_message(self, raw: str) -> dict[str, Any] | None:
        """Parse a raw WebSocket message.

        Protocol messages (Authenticated, Pong, etc.) are logged and ignored.
        Event messages (ROOF_STATUS_CHANGED, etc.) have their data extracted.

        Args:
            raw: Raw message string from WebSocket.

        Returns:
            Parsed event data dict, or None for protocol/unparseable messages.
        """
        try:
            msg = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            _LOGGER.debug("WebSocket non-JSON message: %s", raw[:200])
            return None

        if not isinstance(msg, dict):
            return None

        msg_type = msg.get("type", "")

        # Protocol messages - skip silently
        if msg_type in self._WS_PROTOCOL_TYPES:
            return None

        # Event messages - extract data payload
        if msg_type in self._WS_EVENT_TYPES:
            event_data = msg.get("data")
            if isinstance(event_data, dict):
                _LOGGER.debug("WebSocket event: %s", msg_type)
                return event_data
            return None

        # Unknown message type - log for discovery
        _LOGGER.debug("WebSocket unknown type '%s': %s", msg_type, raw[:500])
        return None

    async def async_disconnect_websocket(self) -> None:
        """Disconnect the WebSocket connection."""
        if self._ws_task and not self._ws_task.done():
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass
            self._ws_task = None

        if self._ws and not self._ws.closed:
            await self._ws.close()
            self._ws = None

    async def async_get_weather_state(self) -> str | None:
        """Get the current weather state from the device.

        Returns:
            Weather state string (e.g., "rain", "sunny") or None.
        """
        if not self._session:
            raise ValueError("Not authenticated. Call async_login() first.")

        url = f"{self.base_url}/api/v1/skye2/comfort/weather/state"
        headers = self._get_headers()

        async with self._session.get(url, headers=headers, ssl=self._ssl_context) as response:
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                data = await response.json()
                # Could be a plain string or a dict with a state key
                if isinstance(data, str):
                    return data
                if isinstance(data, dict):
                    return data.get("state") or data.get("weather_state")
            else:
                text = (await response.text()).strip().strip('"')
                return text if text else None
        return None

    async def async_set_roof_locked(self, locked: bool) -> None:
        """Set the roof lock state.

        Args:
            locked: True to lock, False to unlock.
        """
        if not self._session:
            raise ValueError("Not authenticated. Call async_login() first.")

        url = f"{self.base_url}/api/v1/skye2/roof/lock"
        headers = self._get_headers()
        # Device expects plain text "true" or "false"
        data = "true" if locked else "false"

        async with self._session.put(
            url, data=data, headers=headers, ssl=self._ssl_context
        ) as response:
            response.raise_for_status()

    async def _async_roof_move(self, action: str, value: float) -> None:
        """Send a move command to the roof.

        Args:
            action: "stack" or "tilt".
            value: Target value (percentage for stack, degrees for tilt).
        """
        if not self._session:
            raise ValueError("Not authenticated. Call async_login() first.")

        url = f"{self.base_url}/api/v1/skye2/roof/move"
        headers = self._get_headers()
        payload = {"action": action, "value": value}

        async with self._session.put(
            url, json=payload, headers=headers, ssl=self._ssl_context
        ) as response:
            response.raise_for_status()

    async def async_open_roof(self) -> None:
        """Open the pergola roof (stack to 100%)."""
        await self._async_roof_move("stack", 100)

    async def async_close_roof(self) -> None:
        """Close the pergola roof (stack to 0%)."""
        await self._async_roof_move("stack", 0)

    async def async_stop_roof(self) -> None:
        """Stop the pergola roof."""
        if not self._session:
            raise ValueError("Not authenticated. Call async_login() first.")

        url = f"{self.base_url}/api/v1/skye2/roof/stop"
        headers = self._get_headers()

        async with self._session.put(
            url, json={}, headers=headers, ssl=self._ssl_context
        ) as response:
            response.raise_for_status()

    async def async_set_roof_position(self, position: int) -> None:
        """Set the pergola roof stack to a specific position (0-100%)."""
        await self._async_roof_move("stack", position)

    async def async_set_roof_tilt(self, degrees: float) -> None:
        """Set the pergola roof tilt to a specific angle.

        Args:
            degrees: Tilt angle in degrees (0-125).
        """
        await self._async_roof_move("tilt", degrees)
