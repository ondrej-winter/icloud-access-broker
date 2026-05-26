from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from icloud_access_broker.domain import Capability


@dataclass(frozen=True, slots=True)
class IssueTokenCommand:
    """Application command for issuing a broker token."""

    label: str
    capabilities: frozenset[Capability]
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class IssuedTokenResult:
    """Application result containing token metadata and the one-time secret."""

    token_id: str
    token: str
    label: str
    capabilities: frozenset[Capability]
    created_at: datetime
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class ValidateTokenCommand:
    """Application command for validating a bearer token secret."""

    token: str
    required_capability: Capability | None = None


@dataclass(frozen=True, slots=True)
class TokenValidationResult:
    """Application result for bearer token validation."""

    token_id: str | None
    label: str | None
    capabilities: frozenset[Capability]
    valid: bool
    authorized: bool
    failure_reason: str | None = None


@dataclass(frozen=True, slots=True)
class RevokeTokenCommand:
    """Application command for revoking a broker token."""

    token_id: str


@dataclass(frozen=True, slots=True)
class RevokeTokenResult:
    """Application result for broker token revocation."""

    token_id: str
    revoked: bool
