from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from hmac import compare_digest
from secrets import token_urlsafe
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from icloud_access_broker.domain.capabilities import Capability


@dataclass(frozen=True, slots=True)
class BrokerTokenSecret:
    """One-time bearer secret issued to a downstream broker client."""

    value: str

    @classmethod
    def generate(cls) -> BrokerTokenSecret:
        """Generate a new opaque bearer secret."""
        return cls(token_urlsafe(32))

    def digest(self) -> str:
        """Return a stable digest for storing the secret without retaining it."""
        return sha256(self.value.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class BrokerToken:
    """Broker-issued token metadata used for authorization decisions."""

    token_id: str
    label: str
    capabilities: frozenset[Capability]
    secret_digest: str
    created_at: datetime
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    def is_expired(self, now: datetime) -> bool:
        """Return whether the token is expired at the supplied time."""
        normalized_now = now.astimezone(UTC)
        return self.expires_at is not None and self.expires_at.astimezone(UTC) <= normalized_now

    def is_revoked(self) -> bool:
        """Return whether the token has been revoked."""
        return self.revoked_at is not None

    def matches_secret(self, secret: BrokerTokenSecret) -> bool:
        """Return whether the supplied secret matches this token metadata."""
        return compare_digest(self.secret_digest, secret.digest())

    def revoke(self, revoked_at: datetime) -> BrokerToken:
        """Return a revoked copy of this token."""
        return BrokerToken(
            token_id=self.token_id,
            label=self.label,
            capabilities=self.capabilities,
            secret_digest=self.secret_digest,
            created_at=self.created_at,
            expires_at=self.expires_at,
            revoked_at=revoked_at,
        )
