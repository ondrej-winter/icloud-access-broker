from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from icloud_access_broker.application.dtos import IssuedTokenResult, IssueTokenCommand
from icloud_access_broker.domain import BrokerToken, BrokerTokenSecret

if TYPE_CHECKING:
    from collections.abc import Callable

    from icloud_access_broker.application.ports import TokenStore


class IssueToken:
    """Issue broker tokens with explicit downstream capabilities."""

    def __init__(self, token_store: TokenStore, now: Callable[[], datetime] | None = None) -> None:
        self._token_store = token_store
        self._now = now or (lambda: datetime.now(UTC))

    def execute(self, command: IssueTokenCommand) -> IssuedTokenResult:
        issued_at = self._now()
        secret = BrokerTokenSecret.generate()
        token = BrokerToken(
            token_id=str(uuid4()),
            label=command.label,
            capabilities=command.capabilities,
            secret_digest=secret.digest(),
            created_at=issued_at,
            expires_at=command.expires_at,
        )
        self._token_store.save(token)
        return IssuedTokenResult(
            token_id=token.token_id,
            token=secret.value,
            label=token.label,
            capabilities=token.capabilities,
            created_at=token.created_at,
            expires_at=token.expires_at,
        )
