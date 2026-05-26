from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from icloud_access_broker.application.dtos import TokenValidationResult, ValidateTokenCommand
from icloud_access_broker.domain import BrokerTokenSecret, has_capability

if TYPE_CHECKING:
    from collections.abc import Callable

    from icloud_access_broker.application.ports import TokenStore


class ValidateToken:
    """Validate bearer tokens and required broker capabilities."""

    def __init__(self, token_store: TokenStore, now: Callable[[], datetime] | None = None) -> None:
        self._token_store = token_store
        self._now = now or (lambda: datetime.now(UTC))

    def execute(self, command: ValidateTokenCommand) -> TokenValidationResult:
        secret = BrokerTokenSecret(command.token)
        token = self._token_store.get_by_secret_digest(secret.digest())
        if token is None or not token.matches_secret(secret):
            return _invalid("invalid")
        if token.is_revoked():
            return _invalid("revoked")
        if token.is_expired(self._now()):
            return _invalid("expired")

        authorized = command.required_capability is None or has_capability(
            token.capabilities,
            command.required_capability,
        )
        return TokenValidationResult(
            token_id=token.token_id,
            label=token.label,
            capabilities=token.capabilities,
            valid=True,
            authorized=authorized,
            failure_reason=None if authorized else "insufficient_capability",
        )


def _invalid(reason: str) -> TokenValidationResult:
    return TokenValidationResult(
        token_id=None,
        label=None,
        capabilities=frozenset(),
        valid=False,
        authorized=False,
        failure_reason=reason,
    )
