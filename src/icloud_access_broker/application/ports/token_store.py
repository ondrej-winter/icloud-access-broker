from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from icloud_access_broker.domain import BrokerToken


class TokenStore(Protocol):
    """Application-owned storage boundary for broker token metadata."""

    def save(self, token: BrokerToken) -> None:
        """Store token metadata."""

    def get_by_id(self, token_id: str) -> BrokerToken | None:
        """Return token metadata by id, when present."""

    def get_by_secret_digest(self, secret_digest: str) -> BrokerToken | None:
        """Return token metadata matching a stored secret digest, when present."""
