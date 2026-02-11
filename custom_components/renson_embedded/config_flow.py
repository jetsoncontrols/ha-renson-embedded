"""Config flow for Renson Embedded integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

from .api import RensonClient, RensonConfig
from .const import CONF_USER_TYPE, DOMAIN

_LOGGER = logging.getLogger(__name__)

USER_TYPE_OPTIONS = ["user", "professional", "renson technician"]


class RensonEmbeddedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Renson Embedded."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            config = RensonConfig(
                host=user_input[CONF_HOST],
                user_type=user_input.get(CONF_USER_TYPE, "user"),
                password=user_input.get(CONF_PASSWORD),
            )
            client = RensonClient(config)

            try:
                await client.async_login()
            except aiohttp.ClientResponseError as err:
                _LOGGER.debug("Auth failed: %s", err)
                if err.status == 401:
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "cannot_connect"
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during config flow")
                errors["base"] = "unknown"
            else:
                await client.async_close()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
            finally:
                await client.async_close()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Renson Pergola"): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USER_TYPE, default="user"): vol.In(
                    USER_TYPE_OPTIONS
                ),
                vol.Optional(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
