from __future__ import annotations

from enum import StrEnum


class Capability(StrEnum):
    """Broker-enforced permission granted to a downstream client token."""

    CALENDAR_READ = "calendar:read"
    CALENDAR_WRITE = "calendar:write"
    MAIL_READ = "mail:read"
    MAIL_SEND = "mail:send"


def has_capability(granted_capabilities: frozenset[Capability], required_capability: Capability) -> bool:
    """Return whether the granted capability set includes the required capability."""
    return required_capability in granted_capabilities
