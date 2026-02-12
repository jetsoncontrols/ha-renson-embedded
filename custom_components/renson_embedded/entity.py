"""Base entity for Renson Embedded integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RensonCoordinator


class RensonEntity(CoordinatorEntity[RensonCoordinator]):
    """Base class for Renson entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: RensonCoordinator, entry_id: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.client.host)},
            manufacturer="Renson",
            model="Skye Pergola",
            name="Renson Pergola",
            configuration_url=f"https://{coordinator.client.host}",
        )
        self._entry_id = entry_id
