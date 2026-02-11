"""Sensor platform for Renson Embedded integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    """Set up the Renson sensor platform."""
    coordinator: RensonCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        RensonRoofStateSensor(coordinator, config_entry.entry_id),
        RensonWeatherStateSensor(coordinator, config_entry.entry_id),
    ])


class RensonRoofStateSensor(RensonEntity, SensorEntity):
    """Sensor showing the current roof state (ready, moving, homing, etc.)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "roof_state"

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_roof_state"

    @property
    def native_value(self) -> str | None:
        """Return the current roof state."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("state")


class RensonWeatherStateSensor(RensonEntity, SensorEntity):
    """Sensor showing the current weather state detected by the device."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "weather_state"

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_weather_state"

    @property
    def native_value(self) -> str | None:
        """Return the current weather state."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("weather_state")
