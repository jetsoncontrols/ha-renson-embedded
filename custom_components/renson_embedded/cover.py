"""Platform for Renson Embedded cover integration."""
from __future__ import annotations

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
        return stack == 0

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
        return int(stack)

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        await self.coordinator.client.async_open_roof()
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        await self.coordinator.client.async_close_roof()
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

    # TODO: Tilt properties and commands
    # Device reports tilt in degrees (can exceed 90°). Need to determine
    # full range to map to HA's 0-100 scale.
    # Stack values appear to be 0-1 decimals, need to confirm range.

    @property
    def current_cover_tilt_position(self) -> int | None:
        """Return the current tilt position (0-100)."""
        # TODO: Map device tilt degrees to 0-100 once range is confirmed
        if self.coordinator.data is None:
            return None
        positions = self.coordinator.data.get("current_roof_positions")
        if positions is None:
            return None
        tilt = positions.get("tilt")
        if tilt is None:
            return None
        # Placeholder: raw value, needs proper mapping
        return None

    async def async_open_cover_tilt(self, **kwargs: Any) -> None:
        """Open the cover tilt."""
        # TODO: Implement REST API call to open tilt
        pass

    async def async_close_cover_tilt(self, **kwargs: Any) -> None:
        """Close the cover tilt."""
        # TODO: Implement REST API call to close tilt
        pass

    async def async_stop_cover_tilt(self, **kwargs: Any) -> None:
        """Stop the cover tilt."""
        # TODO: Implement REST API call to stop tilt
        pass

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        """Set the cover tilt to a specific position."""
        # TODO: Map HA 0-100 back to device degrees, implement API call
        pass
