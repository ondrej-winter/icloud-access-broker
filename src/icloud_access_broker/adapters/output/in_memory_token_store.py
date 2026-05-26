from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from icloud_access_broker.domain import BrokerToken


class InMemoryTokenStore:
    """In-memory token store for local development and tests."""

    def __init__(self) -> None:
        self._tokens_by_id: dict[str, BrokerToken] = {}
        self._token_ids_by_secret_digest: dict[str, str] = {}

    def save(self, token: BrokerToken) -> None:
        """Store token metadata in memory."""
        self._tokens_by_id[token.token_id] = token
        self._token_ids_by_secret_digest[token.secret_digest] = token.token_id

    def get_by_id(self, token_id: str) -> BrokerToken | None:
        """Return token metadata by id, when present."""
        return self._tokens_by_id.get(token_id)

    def get_by_secret_digest(self, secret_digest: str) -> BrokerToken | None:
        """Return token metadata matching a stored secret digest, when present."""
        token_id = self._token_ids_by_secret_digest.get(secret_digest)
        if token_id is None:
            return None
        return self._tokens_by_id.get(token_id)
