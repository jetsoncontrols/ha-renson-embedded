"""DataUpdateCoordinator for Renson Embedded integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RensonClient

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class RensonCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that manages data from the Renson device.

    Uses WebSocket for real-time updates with REST polling as fallback.
    REST poll fires every 30s only if no WebSocket data arrives.
    """

    def __init__(self, hass: HomeAssistant, client: RensonClient) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Renson Embedded",
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data via REST (fallback when WebSocket is silent).

        Also starts the WebSocket listener if not already connected.
        """
        # Start WebSocket if not connected
        if not self.client.ws_connected:
            self._start_websocket()

        try:
            data = await self.client.async_get_status()
        except Exception as err:
            raise UpdateFailed(f"Error fetching Renson status: {err}") from err

        # Fetch weather state (separate endpoint)
        try:
            weather = await self.client.async_get_weather_state()
            if weather is not None:
                data["weather_state"] = weather
        except Exception:
            _LOGGER.debug("Failed to fetch weather state", exc_info=True)

        # Preserve WebSocket-only keys (e.g. roof_device from SKYE2_STATUS_CHANGED)
        if self.data:
            for key in ("roof_device",):
                if key in self.data and key not in data:
                    data[key] = self.data[key]

        return data

    def _start_websocket(self) -> None:
        """Start the WebSocket listener as a background task."""
        if self.client._ws_task and not self.client._ws_task.done():
            return

        self.client._ws_task = self.hass.async_create_background_task(
            self.client.async_listen_websocket(self._handle_ws_message),
            name="Renson WebSocket listener",
        )

    def _handle_ws_message(self, data: dict[str, Any]) -> None:
        """Handle an incoming WebSocket message.

        Merges WebSocket data into the current data and pushes the update
        to all listeners, resetting the REST poll timer.
        """
        if self.data is None:
            # No REST data yet; store what we got and let REST fill the rest
            self.async_set_updated_data(data)
            return

        merged = {**self.data, **data}
        self.async_set_updated_data(merged)

    async def async_shutdown(self) -> None:
        """Disconnect WebSocket on coordinator shutdown."""
        await self.client.async_disconnect_websocket()
        await super().async_shutdown()
