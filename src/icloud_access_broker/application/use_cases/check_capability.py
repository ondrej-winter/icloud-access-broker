from icloud_access_broker.application.dtos import AuthorizationDecision, CheckCapabilityCommand
from icloud_access_broker.domain import has_capability


class CheckCapability:
    """Check whether a downstream token grants a required broker capability."""

    def execute(self, command: CheckCapabilityCommand) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=has_capability(command.granted_capabilities, command.required_capability),
            required_capability=command.required_capability,
        )
