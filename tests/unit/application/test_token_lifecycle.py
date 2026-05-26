from datetime import UTC, datetime, timedelta

from icloud_access_broker.adapters.output import InMemoryTokenStore
from icloud_access_broker.application.dtos import IssueTokenCommand, RevokeTokenCommand, ValidateTokenCommand
from icloud_access_broker.application.use_cases import IssueToken, RevokeToken, ValidateToken
from icloud_access_broker.domain import Capability

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def test_issued_token_validates_with_granted_capability() -> None:
    store = InMemoryTokenStore()
    issued = IssueToken(store, now=lambda: NOW).execute(
        IssueTokenCommand(label="calendar agent", capabilities=frozenset({Capability.CALENDAR_READ}))
    )

    result = ValidateToken(store, now=lambda: NOW).execute(
        ValidateTokenCommand(token=issued.token, required_capability=Capability.CALENDAR_READ)
    )

    assert result.valid
    assert result.authorized
    assert result.token_id == issued.token_id
    assert result.capabilities == frozenset({Capability.CALENDAR_READ})


def test_validation_denies_missing_capability() -> None:
    store = InMemoryTokenStore()
    issued = IssueToken(store, now=lambda: NOW).execute(
        IssueTokenCommand(label="calendar agent", capabilities=frozenset({Capability.CALENDAR_READ}))
    )

    result = ValidateToken(store, now=lambda: NOW).execute(
        ValidateTokenCommand(token=issued.token, required_capability=Capability.MAIL_SEND)
    )

    assert result.valid
    assert not result.authorized
    assert result.failure_reason == "insufficient_capability"


def test_validation_rejects_expired_token() -> None:
    store = InMemoryTokenStore()
    issued = IssueToken(store, now=lambda: NOW).execute(
        IssueTokenCommand(
            label="calendar agent",
            capabilities=frozenset({Capability.CALENDAR_READ}),
            expires_at=NOW + timedelta(minutes=5),
        )
    )

    result = ValidateToken(store, now=lambda: NOW + timedelta(minutes=6)).execute(
        ValidateTokenCommand(token=issued.token, required_capability=Capability.CALENDAR_READ)
    )

    assert not result.valid
    assert result.failure_reason == "expired"


def test_revoked_token_no_longer_validates() -> None:
    store = InMemoryTokenStore()
    issued = IssueToken(store, now=lambda: NOW).execute(
        IssueTokenCommand(label="calendar agent", capabilities=frozenset({Capability.CALENDAR_READ}))
    )

    revoked = RevokeToken(store, now=lambda: NOW + timedelta(minutes=1)).execute(
        RevokeTokenCommand(token_id=issued.token_id)
    )
    result = ValidateToken(store, now=lambda: NOW + timedelta(minutes=2)).execute(
        ValidateTokenCommand(token=issued.token, required_capability=Capability.CALENDAR_READ)
    )

    assert revoked.revoked
    assert not result.valid
    assert result.failure_reason == "revoked"
