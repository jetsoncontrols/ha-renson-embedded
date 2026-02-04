"""Config flow for Renson Embedded integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class RensonEmbeddedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Renson Embedded."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # TODO: Validate the connection to the device

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Renson Pergola"): str,
                vol.Required(CONF_HOST): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
