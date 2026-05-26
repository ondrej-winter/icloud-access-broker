from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from icloud_access_broker.application.dtos import RevokeTokenCommand, RevokeTokenResult

if TYPE_CHECKING:
    from collections.abc import Callable

    from icloud_access_broker.application.ports import TokenStore


class RevokeToken:
    """Revoke a broker token by id."""

    def __init__(self, token_store: TokenStore, now: Callable[[], datetime] | None = None) -> None:
        self._token_store = token_store
        self._now = now or (lambda: datetime.now(UTC))

    def execute(self, command: RevokeTokenCommand) -> RevokeTokenResult:
        token = self._token_store.get_by_id(command.token_id)
        if token is None:
            return RevokeTokenResult(token_id=command.token_id, revoked=False)

        self._token_store.save(token.revoke(self._now()))
        return RevokeTokenResult(token_id=command.token_id, revoked=True)
