from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime  # noqa: TC003 - Pydantic needs runtime access to rebuild response models.
from hmac import compare_digest
from typing import TYPE_CHECKING, Annotated, Protocol

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict

from icloud_access_broker.adapters.output import InMemoryTokenStore
from icloud_access_broker.application.dtos import (
    AppSettings,
    IssueTokenCommand,
    RevokeTokenCommand,
    TokenValidationResult,
    ValidateTokenCommand,
)
from icloud_access_broker.application.use_cases import GetServiceInfo, IssueToken, RevokeToken, ValidateToken
from icloud_access_broker.domain import Capability

if TYPE_CHECKING:
    from collections.abc import Callable

    from icloud_access_broker.application.dtos import ServiceInfo
    from icloud_access_broker.application.ports import TokenStore


class ServiceInfoProvider(Protocol):
    """Local HTTP adapter protocol for retrieving service metadata."""

    def execute(self) -> ServiceInfo:
        """Return service metadata."""


class HealthResponse(BaseModel):
    """HTTP response model for broker health checks."""

    status: str


class VersionResponse(BaseModel):
    """HTTP response model for broker service metadata."""

    model_config = ConfigDict(frozen=True)

    name: str
    package_name: str
    import_name: str


class IssueTokenRequest(BaseModel):
    """HTTP request model for issuing a broker token."""

    model_config = ConfigDict(frozen=True)

    label: str
    capabilities: frozenset[Capability]
    expires_at: datetime | None = None


class IssueTokenResponse(BaseModel):
    """HTTP response model for a newly issued broker token."""

    model_config = ConfigDict(frozen=True)

    token_id: str
    token: str
    label: str
    capabilities: frozenset[Capability]
    created_at: datetime
    expires_at: datetime | None = None


class RevokeTokenResponse(BaseModel):
    """HTTP response model for broker token revocation."""

    model_config = ConfigDict(frozen=True)

    token_id: str
    revoked: bool


class CapabilityProofResponse(BaseModel):
    """HTTP response model proving bearer-token capability enforcement."""

    model_config = ConfigDict(frozen=True)

    token_id: str
    label: str
    capability: Capability


@dataclass(frozen=True, slots=True)
class TokenUseCases:
    """HTTP adapter container for token lifecycle use cases."""

    issue_token: IssueToken
    validate_token: ValidateToken
    revoke_token: RevokeToken


def create_app(
    service_info_provider: ServiceInfoProvider | None = None,
    token_store: TokenStore | None = None,
    settings: AppSettings | None = None,
) -> FastAPI:
    """Create the FastAPI application for the broker REST API."""
    provider = service_info_provider or GetServiceInfo()
    tokens = token_store or InMemoryTokenStore()
    app_settings = settings or AppSettings(admin_secret="")
    token_use_cases = TokenUseCases(
        issue_token=IssueToken(tokens),
        validate_token=ValidateToken(tokens),
        revoke_token=RevokeToken(tokens),
    )
    app = FastAPI(
        title="iCloud Access Broker",
        summary="Policy-enforcing broker for personal iCloud access.",
        version="0.1.0",
    )

    register_service_routes(app, provider)
    register_token_routes(app, app_settings, token_use_cases)

    return app


def register_service_routes(app: FastAPI, provider: ServiceInfoProvider) -> None:
    """Register public service metadata routes."""

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/version", response_model=VersionResponse)
    def version() -> VersionResponse:
        service_info = provider.execute()
        return VersionResponse(
            name=service_info.name,
            package_name=service_info.package_name,
            import_name=service_info.import_name,
        )


def register_token_routes(app: FastAPI, settings: AppSettings, token_use_cases: TokenUseCases) -> None:
    """Register admin token lifecycle routes and bearer-token proof routes."""
    require_admin_secret = build_admin_secret_dependency(settings)
    require_calendar_read = build_capability_dependency(token_use_cases, Capability.CALENDAR_READ)

    register_admin_token_routes(app, token_use_cases, require_admin_secret)
    register_capability_proof_routes(app, require_calendar_read)


def build_admin_secret_dependency(settings: AppSettings) -> Callable[[str | None], None]:
    """Build a FastAPI dependency that checks the local admin secret."""

    def require_admin_secret(x_admin_secret: Annotated[str | None, Header()] = None) -> None:
        if (
            not settings.admin_secret
            or x_admin_secret is None
            or not compare_digest(x_admin_secret, settings.admin_secret)
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin secret")

    return require_admin_secret


def build_capability_dependency(
    token_use_cases: TokenUseCases,
    required_capability: Capability,
) -> Callable[[str | None], TokenValidationResult]:
    """Build a FastAPI dependency that validates bearer tokens for a capability."""

    def dependency(authorization: Annotated[str | None, Header()] = None) -> TokenValidationResult:
        bearer_prefix = "Bearer "
        if authorization is None or not authorization.startswith(bearer_prefix):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

        result = token_use_cases.validate_token.execute(
            ValidateTokenCommand(
                token=authorization.removeprefix(bearer_prefix),
                required_capability=required_capability,
            )
        )
        if not result.valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")
        if not result.authorized:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient capability")
        return result

    return dependency


def register_admin_token_routes(
    app: FastAPI,
    token_use_cases: TokenUseCases,
    require_admin_secret: Callable[[str | None], None],
) -> None:
    """Register admin-secret-protected token lifecycle routes."""

    @app.post(
        "/admin/tokens",
        response_model=IssueTokenResponse,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_admin_secret)],
    )
    def create_token(request: IssueTokenRequest) -> IssueTokenResponse:
        issued = token_use_cases.issue_token.execute(
            IssueTokenCommand(
                label=request.label,
                capabilities=request.capabilities,
                expires_at=request.expires_at,
            )
        )
        return IssueTokenResponse(
            token_id=issued.token_id,
            token=issued.token,
            label=issued.label,
            capabilities=issued.capabilities,
            created_at=issued.created_at,
            expires_at=issued.expires_at,
        )

    @app.delete(
        "/admin/tokens/{token_id}",
        response_model=RevokeTokenResponse,
        dependencies=[Depends(require_admin_secret)],
    )
    def delete_token(token_id: str) -> RevokeTokenResponse:
        result = token_use_cases.revoke_token.execute(RevokeTokenCommand(token_id=token_id))
        return RevokeTokenResponse(token_id=result.token_id, revoked=result.revoked)


def register_capability_proof_routes(
    app: FastAPI,
    require_calendar_read: Callable[[str | None], TokenValidationResult],
) -> None:
    """Register routes that prove bearer-token capability enforcement."""

    @app.get("/capabilities/calendar/read", response_model=CapabilityProofResponse)
    def prove_calendar_read(
        authorization: Annotated[str | None, Header()] = None,
    ) -> CapabilityProofResponse:
        principal = require_calendar_read(authorization)
        if principal.token_id is None or principal.label is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")
        return CapabilityProofResponse(
            token_id=principal.token_id,
            label=principal.label,
            capability=Capability.CALENDAR_READ,
        )
