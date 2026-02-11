"""Button platform for Renson Embedded integration."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    """Set up the Renson button platform."""
    coordinator: RensonCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        RensonFullyOpenButton(coordinator, config_entry.entry_id),
        RensonFullyCloseButton(coordinator, config_entry.entry_id),
    ])


class RensonFullyOpenButton(RensonEntity, ButtonEntity):
    """Button to fully open the pergola roof."""

    _attr_translation_key = "fully_open"

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_fully_open"

    async def async_press(self) -> None:
        """Fully open the roof."""
        await self.coordinator.client.async_fully_open_roof()
        await self.coordinator.async_request_refresh()


class RensonFullyCloseButton(RensonEntity, ButtonEntity):
    """Button to fully close the pergola roof."""

    _attr_translation_key = "fully_close"

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_fully_close"

    async def async_press(self) -> None:
        """Fully close the roof."""
        await self.coordinator.client.async_fully_close_roof()
        await self.coordinator.async_request_refresh()
