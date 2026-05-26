import uvicorn

from icloud_access_broker.adapters.input.env_settings_adapter import EnvSettingsAdapter
from icloud_access_broker.adapters.input.http.app import create_app


def main() -> None:
    """Run the development HTTP server."""
    settings = EnvSettingsAdapter().load()
    uvicorn.run(create_app(settings=settings), host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
