from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ServiceInfo:
    """Application boundary result describing the broker service."""

    name: str
    package_name: str
    import_name: str
