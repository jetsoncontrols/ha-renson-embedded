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


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Renson Embedded cover platform."""
    # TODO: Get the client from hass.data
    # client = hass.data[DOMAIN][config_entry.entry_id]

    # TODO: Create cover entities based on device capabilities
    async_add_entities([RensonPergolaRoof(config_entry)], True)


class RensonPergolaRoof(CoverEntity):
    """Representation of a Renson Pergola motorized roof."""

    _attr_device_class = CoverDeviceClass.AWNING
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the cover."""
        self._attr_name = config_entry.data.get("name", "Renson Pergola Roof")
        self._attr_unique_id = f"{config_entry.entry_id}_roof"
        self._attr_is_closed = None
        self._attr_current_cover_position = None

    async def async_update(self) -> None:
        """Fetch new state data for this cover."""
        # TODO: Implement update logic using the client
        pass

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        # TODO: Implement open logic
        pass

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        # TODO: Implement close logic
        pass

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        # TODO: Implement stop logic
        pass

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        # TODO: Implement position logic
        pass
