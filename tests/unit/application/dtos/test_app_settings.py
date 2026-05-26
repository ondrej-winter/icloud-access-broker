from icloud_access_broker.application.dtos import AppSettings

ADMIN_HEADER_VALUE = "local-admin-header-value"


def test_app_settings_preserves_admin_secret() -> None:
    settings = AppSettings(admin_secret=ADMIN_HEADER_VALUE)

    assert settings.admin_secret == ADMIN_HEADER_VALUE
