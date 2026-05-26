from datetime import UTC, datetime, timedelta

from icloud_access_broker.domain import BrokerToken, BrokerTokenSecret, Capability

NOW = datetime(2026, 1, 1, tzinfo=UTC)
BROKER_IDENTIFIER = "broker-token-id"


def test_token_secret_matches_stored_digest_without_storing_raw_value() -> None:
    secret = BrokerTokenSecret("example-token")
    token = BrokerToken(
        token_id=BROKER_IDENTIFIER,
        label="agent",
        capabilities=frozenset({Capability.CALENDAR_READ}),
        secret_digest=secret.digest(),
        created_at=NOW,
    )

    assert token.matches_secret(secret)
    assert token.secret_digest != secret.value


def test_token_reports_expired_when_expiry_is_not_in_future() -> None:
    token = BrokerToken(
        token_id=BROKER_IDENTIFIER,
        label="agent",
        capabilities=frozenset({Capability.CALENDAR_READ}),
        secret_digest=BrokerTokenSecret("example-token").digest(),
        created_at=NOW - timedelta(hours=2),
        expires_at=NOW - timedelta(seconds=1),
    )

    assert token.is_expired(NOW)


def test_revoke_returns_revoked_token_copy() -> None:
    token = BrokerToken(
        token_id=BROKER_IDENTIFIER,
        label="agent",
        capabilities=frozenset({Capability.CALENDAR_READ}),
        secret_digest=BrokerTokenSecret("example-token").digest(),
        created_at=NOW,
    )

    revoked = token.revoke(NOW + timedelta(minutes=1))

    assert revoked.is_revoked()
    assert not token.is_revoked()
