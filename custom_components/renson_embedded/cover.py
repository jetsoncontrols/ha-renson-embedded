"""Platform for Renson Embedded cover integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RensonCoordinator
from .entity import RensonEntity

_LOGGER = logging.getLogger(__name__)

TILT_MAX_DEGREES = 125


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Renson Embedded cover platform."""
    coordinator: RensonCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([RensonPergolaRoof(coordinator, config_entry)])


class RensonPergolaRoof(RensonEntity, CoverEntity):
    """Representation of a Renson Pergola motorized roof."""

    _attr_device_class = CoverDeviceClass.AWNING
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.OPEN_TILT
        | CoverEntityFeature.CLOSE_TILT
        | CoverEntityFeature.STOP_TILT
        | CoverEntityFeature.SET_TILT_POSITION
    )

    def __init__(
        self, coordinator: RensonCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the cover."""
        super().__init__(coordinator, config_entry.entry_id)
        self._attr_name = config_entry.data.get("name", "Renson Pergola Roof")
        self._attr_unique_id = f"{config_entry.entry_id}_roof"

    def _get_roof_device(self) -> dict | None:
        """Get the roof_device dict from SKYE2_STATUS_CHANGED data."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("roof_device")

    @property
    def is_opening(self) -> bool | None:
        """Return True if the cover is opening."""
        roof = self._get_roof_device()
        if roof is None:
            return None
        direction = roof.get("direction", "idle")
        _LOGGER.debug("Roof direction: %s, state: %s", direction, roof.get("state"))
        if roof.get("state") != "moving":
            return False
        return direction in ("tilting_open", "stacking")

    @property
    def is_closing(self) -> bool | None:
        """Return True if the cover is closing."""
        roof = self._get_roof_device()
        if roof is None:
            return None
        direction = roof.get("direction", "idle")
        if roof.get("state") != "moving":
            return False
        return direction in ("tilting_close", "unstacking")

    @property
    def is_closed(self) -> bool | None:
        """Return True if the cover is closed."""
        if self.coordinator.data is None:
            return None
        positions = self.coordinator.data.get("current_roof_positions")
        if positions is None:
            return None
        stack = positions.get("stack")
        if stack is None:
            return None
        return round(stack) == 0

    @property
    def current_cover_position(self) -> int | None:
        """Return the current cover position (0-100)."""
        if self.coordinator.data is None:
            return None
        positions = self.coordinator.data.get("current_roof_positions")
        if positions is None:
            return None
        stack = positions.get("stack")
        if stack is None:
            return None
        _LOGGER.debug("Slide position: %s%%", stack)
        return round(stack)

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        await self.coordinator.client.async_open_roof()
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover (tilt to 0, slide closes automatically)."""
        await self.coordinator.client.async_set_roof_tilt(0)
        await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        await self.coordinator.client.async_stop_roof()
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        position = kwargs.get("position", 0)
        await self.coordinator.client.async_set_roof_position(position)
        await self.coordinator.async_request_refresh()

    @property
    def current_cover_tilt_position(self) -> int | None:
        """Return the current tilt position (0-100, mapped from 0-125 degrees)."""
        if self.coordinator.data is None:
            return None
        positions = self.coordinator.data.get("current_roof_positions")
        if positions is None:
            return None
        tilt = positions.get("tilt")
        if tilt is None:
            return None
        _LOGGER.debug("Tilt angle: %s°", tilt)
        return self._degrees_to_ha(tilt)

    async def async_open_cover_tilt(self, **kwargs: Any) -> None:
        """Open the cover tilt to 90 degrees."""
        await self.coordinator.client.async_set_roof_tilt(90)
        await self.coordinator.async_request_refresh()

    async def async_close_cover_tilt(self, **kwargs: Any) -> None:
        """Close the cover tilt to 0 degrees."""
        await self.coordinator.client.async_set_roof_tilt(0)
        await self.coordinator.async_request_refresh()

    async def async_stop_cover_tilt(self, **kwargs: Any) -> None:
        """Stop the cover tilt."""
        await self.coordinator.client.async_stop_roof()
        await self.coordinator.async_request_refresh()

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        """Set the cover tilt to a specific position."""
        position = kwargs.get("tilt_position", 0)
        degrees = self._ha_to_degrees(position)
        await self.coordinator.client.async_set_roof_tilt(degrees)
        await self.coordinator.async_request_refresh()

    @staticmethod
    def _degrees_to_ha(degrees: float) -> int:
        """Convert device degrees (0-125) to HA position (0-100)."""
        return min(100, max(0, round(degrees / TILT_MAX_DEGREES * 100)))

    @staticmethod
    def _ha_to_degrees(position: int) -> float:
        """Convert HA position (0-100) to device degrees (0-125)."""
        position = min(100, max(0, position))
        return round(position / 100 * TILT_MAX_DEGREES, 1)
