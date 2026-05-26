from __future__ import annotations

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from icloud_access_broker.application.exceptions import ConfigurationError

BLANK_TEXT_ERROR = "must not be blank"
ENV_PREFIX = "ICLOUD_ACCESS_BROKER"
ADMIN_SECRET_ALIAS = f"{ENV_PREFIX}_ADMIN_SECRET"
INVALID_CONFIGURATION_ERROR = "Invalid runtime configuration for iCloud Access Broker."


class EnvSettings(BaseSettings):
    """Adapter-owned environment settings model."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )

    admin_secret: str = Field(alias="ICLOUD_ACCESS_BROKER_ADMIN_SECRET")

    @field_validator("admin_secret", mode="before")
    @classmethod
    def validate_non_empty_text(cls, value: object) -> object:
        """Normalize and reject blank text settings."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError(BLANK_TEXT_ERROR)
            return stripped
        return value


def load_settings_from_env() -> EnvSettings:
    """Load and validate environment-backed settings."""
    try:
        return EnvSettings()  # type: ignore[call-arg]
    except ValidationError as exc:
        raise ConfigurationError(INVALID_CONFIGURATION_ERROR) from exc
