from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from icloud_access_broker.application.dtos.service_info import ServiceInfo


class ServiceInfoProvider(Protocol):
    """Input port for retrieving service metadata."""

    def execute(self) -> ServiceInfo:
        """Return service metadata."""
