"""Button platform for Renson Embedded integration."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RensonCoordinator
from .entity import RensonEntity

_LOGGER = logging.getLogger(__name__)

_OPENING_DIRECTIONS = {"tilting_open", "stacking"}
_CLOSING_DIRECTIONS = {"tilting_close", "unstacking"}


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
        RensonCycleButton(coordinator, config_entry.entry_id),
    ])


class RensonFullyOpenButton(RensonEntity, ButtonEntity):
    """Button to fully open the pergola roof (stack to 100%)."""

    _attr_translation_key = "fully_open"

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_fully_open"

    async def async_press(self) -> None:
        """Fully open the roof."""
        await self.coordinator.client.async_open_roof()
        await self.coordinator.async_request_refresh()


class RensonFullyCloseButton(RensonEntity, ButtonEntity):
    """Button to fully close the pergola roof (tilt to 0)."""

    _attr_translation_key = "fully_close"

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_fully_close"

    async def async_press(self) -> None:
        """Fully close the roof."""
        await self.coordinator.client.async_set_roof_tilt(0)
        await self.coordinator.async_request_refresh()


class RensonCycleButton(RensonEntity, ButtonEntity):
    """Button that cycles: open → stop → close → stop.

    Logic:
    - If moving → stop
    - If stopped and last direction was opening (or fully open) → close everything
    - If stopped and last direction was closing (or fully closed) → open
    """

    _attr_translation_key = "cycle"

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_cycle"
        self._last_direction: str = "closing"  # default: next press will open

    def _handle_coordinator_update(self) -> None:
        """Track last movement direction from coordinator data."""
        if self.coordinator.data:
            roof = self.coordinator.data.get("roof_device")
            if roof and roof.get("state") == "moving":
                direction = roof.get("direction", "idle")
                if direction in _OPENING_DIRECTIONS:
                    self._last_direction = "opening"
                elif direction in _CLOSING_DIRECTIONS:
                    self._last_direction = "closing"
        super()._handle_coordinator_update()

    async def async_press(self) -> None:
        """Cycle through open/stop/close/stop."""
        roof = None
        stack = 0.0
        tilt = 0.0

        if self.coordinator.data:
            roof = self.coordinator.data.get("roof_device")
            positions = self.coordinator.data.get("current_roof_positions", {})
            stack = positions.get("stack", 0.0)
            tilt = positions.get("tilt", 0.0)

        is_moving = roof and roof.get("state") == "moving"

        if is_moving:
            _LOGGER.debug("Cycle button: stopping")
            await self.coordinator.client.async_stop_roof()
        elif self._last_direction == "opening" or (round(stack) >= 100):
            _LOGGER.debug("Cycle button: closing everything")
            await self.coordinator.client.async_set_roof_tilt(0)
            self._last_direction = "closing"
        else:
            _LOGGER.debug("Cycle button: opening")
            await self.coordinator.client.async_open_roof()
            self._last_direction = "opening"

        await self.coordinator.async_request_refresh()
