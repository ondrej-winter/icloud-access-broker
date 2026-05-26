from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from icloud_access_broker.domain import Capability


@dataclass(frozen=True, slots=True)
class CheckCapabilityCommand:
    """Application boundary command for checking a broker token capability."""

    granted_capabilities: frozenset[Capability]
    required_capability: Capability


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """Application boundary result for a capability authorization check."""

    allowed: bool
    required_capability: Capability
