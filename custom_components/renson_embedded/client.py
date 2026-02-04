"""Client for communicating with Renson Embedded device."""
from __future__ import annotations

import asyncio
from typing import Any


class RensonClient:
    """Client to communicate with Renson Embedded device via REST API."""

    def __init__(self, host: str) -> None:
        """Initialize the client."""
        self.host = host
        self.base_url = f"http://{host}"

    async def async_get_status(self) -> dict[str, Any]:
        """Get the current status of the device."""
        # TODO: Implement REST API call to get status
        pass

    async def async_open(self) -> None:
        """Open the pergola roof."""
        # TODO: Implement REST API call to open
        pass

    async def async_close(self) -> None:
        """Close the pergola roof."""
        # TODO: Implement REST API call to close
        pass

    async def async_stop(self) -> None:
        """Stop the pergola roof."""
        # TODO: Implement REST API call to stop
        pass

    async def async_set_position(self, position: int) -> None:
        """Set the pergola roof to a specific position."""
        # TODO: Implement REST API call to set position
        pass
