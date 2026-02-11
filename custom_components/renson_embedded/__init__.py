"""The Renson Embedded integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant

from .api import RensonClient, RensonConfig
from .const import CONF_USER_TYPE, DOMAIN
from .coordinator import RensonCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.COVER, Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Renson Embedded from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    config = RensonConfig(
        host=entry.data[CONF_HOST],
        user_type=entry.data.get(CONF_USER_TYPE, "user"),
        password=entry.data.get(CONF_PASSWORD),
    )
    client = RensonClient(config)
    await client.async_login()

    coordinator = RensonCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: RensonCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.async_close()

    return unload_ok
