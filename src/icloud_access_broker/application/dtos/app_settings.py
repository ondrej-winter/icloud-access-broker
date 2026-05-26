from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppSettings:
    """Application-owned runtime settings for the broker."""

    admin_secret: str
