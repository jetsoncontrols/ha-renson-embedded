"""Binary sensor platform for Renson Embedded integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Set up the Renson binary sensor platform."""
    coordinator: RensonCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        RensonFullyClosedSensor(coordinator, config_entry.entry_id),
        RensonFullyOpenedSensor(coordinator, config_entry.entry_id),
    ])


class RensonFullyClosedSensor(RensonEntity, BinarySensorEntity):
    """Binary sensor that is on when the roof is fully closed (stack=0, tilt=0)."""

    _attr_translation_key = "fully_closed"

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_fully_closed"

    @property
    def is_on(self) -> bool | None:
        """Return True if fully closed."""
        if self.coordinator.data is None:
            return None
        positions = self.coordinator.data.get("current_roof_positions")
        if positions is None:
            return None
        stack = positions.get("stack")
        tilt = positions.get("tilt")
        if stack is None or tilt is None:
            return None
        return round(stack) == 0 and round(tilt) == 0


class RensonFullyOpenedSensor(RensonEntity, BinarySensorEntity):
    """Binary sensor that is on when the roof is fully open (stack=100, tilt=90)."""

    _attr_translation_key = "fully_opened"

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_fully_opened"

    @property
    def is_on(self) -> bool | None:
        """Return True if fully opened."""
        if self.coordinator.data is None:
            return None
        positions = self.coordinator.data.get("current_roof_positions")
        if positions is None:
            return None
        stack = positions.get("stack")
        tilt = positions.get("tilt")
        if stack is None or tilt is None:
            return None
        return round(stack) >= 100 and round(tilt) >= 90
