"""Switch platform for Renson Embedded integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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
    """Set up the Renson switch platform."""
    coordinator: RensonCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([RensonRoofLockSwitch(coordinator, config_entry.entry_id)])


class RensonRoofLockSwitch(RensonEntity, SwitchEntity):
    """Switch to lock/unlock the pergola roof."""

    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_translation_key = "roof_lock"

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_roof_lock"

    @property
    def is_on(self) -> bool | None:
        """Return True if the roof is locked."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("locked")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Lock the roof."""
        await self.coordinator.client.async_set_roof_locked(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Unlock the roof."""
        await self.coordinator.client.async_set_roof_locked(False)
        await self.coordinator.async_request_refresh()
