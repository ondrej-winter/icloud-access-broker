from dataclasses import dataclass

from fastapi.testclient import TestClient

from icloud_access_broker.adapters.input.http import create_app
from icloud_access_broker.application.dtos import AppSettings, ServiceInfo

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
ADMIN_HEADER_VALUE = "local-admin-header-value"


@dataclass(frozen=True, slots=True)
class StubServiceInfoProvider:
    service_info: ServiceInfo

    def execute(self) -> ServiceInfo:
        return self.service_info


def test_health_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ok"}


def test_version_returns_service_metadata() -> None:
    client = TestClient(create_app(StubServiceInfoProvider(ServiceInfo("Example", "example", "example"))))

    response = client.get("/version")

    assert response.status_code == HTTP_OK
    assert response.json() == {"name": "Example", "package_name": "example", "import_name": "example"}


def test_admin_secret_required_to_issue_token() -> None:
    client = TestClient(create_app(settings=AppSettings(admin_secret=ADMIN_HEADER_VALUE)))

    response = client.post(
        "/admin/tokens",
        json={"label": "calendar agent", "capabilities": ["calendar:read"]},
    )

    assert response.status_code == HTTP_UNAUTHORIZED


def test_issued_token_can_access_matching_capability_route() -> None:
    client = TestClient(create_app(settings=AppSettings(admin_secret=ADMIN_HEADER_VALUE)))

    issue_response = client.post(
        "/admin/tokens",
        headers={"X-Admin-Secret": ADMIN_HEADER_VALUE},
        json={"label": "calendar agent", "capabilities": ["calendar:read"]},
    )
    token = issue_response.json()["token"]

    response = client.get("/capabilities/calendar/read", headers={"Authorization": f"Bearer {token}"})

    assert issue_response.status_code == HTTP_CREATED
    assert response.status_code == HTTP_OK
    assert response.json()["label"] == "calendar agent"
    assert response.json()["capability"] == "calendar:read"


def test_bearer_token_with_missing_capability_is_forbidden() -> None:
    client = TestClient(create_app(settings=AppSettings(admin_secret=ADMIN_HEADER_VALUE)))
    issue_response = client.post(
        "/admin/tokens",
        headers={"X-Admin-Secret": ADMIN_HEADER_VALUE},
        json={"label": "mail agent", "capabilities": ["mail:read"]},
    )
    token = issue_response.json()["token"]

    response = client.get("/capabilities/calendar/read", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == HTTP_FORBIDDEN


def test_revoked_token_is_rejected() -> None:
    client = TestClient(create_app(settings=AppSettings(admin_secret=ADMIN_HEADER_VALUE)))
    issue_response = client.post(
        "/admin/tokens",
        headers={"X-Admin-Secret": ADMIN_HEADER_VALUE},
        json={"label": "calendar agent", "capabilities": ["calendar:read"]},
    )
    issued = issue_response.json()

    revoke_response = client.delete(
        f"/admin/tokens/{issued['token_id']}",
        headers={"X-Admin-Secret": ADMIN_HEADER_VALUE},
    )
    response = client.get("/capabilities/calendar/read", headers={"Authorization": f"Bearer {issued['token']}"})

    assert revoke_response.status_code == HTTP_OK
    assert revoke_response.json() == {"token_id": issued["token_id"], "revoked": True}
    assert response.status_code == HTTP_UNAUTHORIZED
