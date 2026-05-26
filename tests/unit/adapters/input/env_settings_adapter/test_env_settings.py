import pytest

from icloud_access_broker.adapters.input.env_settings_adapter import EnvSettingsAdapter
from icloud_access_broker.adapters.input.env_settings_adapter.settings import ADMIN_SECRET_ALIAS
from icloud_access_broker.application.exceptions import ConfigurationError

ADMIN_HEADER_VALUE = "local-admin-header-value"


def test_missing_admin_secret_raises_configuration_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ADMIN_SECRET_ALIAS, raising=False)

    with pytest.raises(ConfigurationError, match="Invalid runtime configuration"):
        EnvSettingsAdapter().load()


@pytest.mark.parametrize("raw_value", ["", "   "])
def test_blank_admin_secret_raises_configuration_error(monkeypatch: pytest.MonkeyPatch, raw_value: str) -> None:
    monkeypatch.setenv(ADMIN_SECRET_ALIAS, raw_value)

    with pytest.raises(ConfigurationError, match="Invalid runtime configuration"):
        EnvSettingsAdapter().load()


def test_valid_admin_secret_loads_app_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ADMIN_SECRET_ALIAS, f"  {ADMIN_HEADER_VALUE}  ")

    settings = EnvSettingsAdapter().load()

    assert settings.admin_secret == ADMIN_HEADER_VALUE


def test_unrelated_environment_variables_are_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ADMIN_SECRET_ALIAS, ADMIN_HEADER_VALUE)
    monkeypatch.setenv("UNRELATED_SETTING", "ignored")

    settings = EnvSettingsAdapter().load()

    assert settings.admin_secret == ADMIN_HEADER_VALUE
