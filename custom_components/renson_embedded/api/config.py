"""Configuration for Renson client."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class RensonConfig:
    """Configuration for RensonClient.

    This encapsulates all configuration options for the client with sensible defaults.
    """

    host: str
    """IP address or hostname of the Renson device (required)."""

    path: str = "/api/v1/roof"
    """API path for the controlled device. Default: '/api/v1/roof' for roof control.

    To discover the correct path:
    1. Open the Renson web UI in a browser (https://<host>/roof)
    2. Open browser DevTools (F12) and go to Network tab
    3. Interact with the roof controls in the UI
    4. Look for API calls in the Network tab to find the correct endpoint
    """

    user_type: Literal["user", "professional", "renson technician"] = "user"
    """User type for authentication. Default: 'user'."""

    password: str | None = None
    """Password for authentication (if required)."""

    port: int = 443
    """HTTPS port. Default: 443."""

    verify_ssl: bool = False
    """Whether to verify SSL certificates. Default: False (Renson uses self-signed certs)."""

    timeout: int = 30
    """Request timeout in seconds. Default: 30."""

    @property
    def base_url(self) -> str:
        """Get the base URL for API requests."""
        if self.port == 443:
            return f"https://{self.host}"
        return f"https://{self.host}:{self.port}"

    def __post_init__(self) -> None:
        """Validate and normalize configuration after initialization."""
        # Normalize user_type to lowercase
        if isinstance(self.user_type, str):
            self.user_type = self.user_type.lower()

        # Validate user_type
        valid_types = ["user", "professional", "renson technician"]
        if self.user_type not in valid_types:
            raise ValueError(
                f"Invalid user_type: {self.user_type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )
