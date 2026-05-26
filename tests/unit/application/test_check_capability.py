from icloud_access_broker.application.dtos import CheckCapabilityCommand
from icloud_access_broker.application.use_cases import CheckCapability
from icloud_access_broker.domain import Capability


def test_allows_required_capability_when_granted() -> None:
    decision = CheckCapability().execute(
        CheckCapabilityCommand(
            granted_capabilities=frozenset({Capability.CALENDAR_READ}),
            required_capability=Capability.CALENDAR_READ,
        )
    )

    assert decision.allowed
    assert decision.required_capability == Capability.CALENDAR_READ


def test_denies_required_capability_when_missing() -> None:
    decision = CheckCapability().execute(
        CheckCapabilityCommand(
            granted_capabilities=frozenset({Capability.MAIL_READ}),
            required_capability=Capability.MAIL_SEND,
        )
    )

    assert not decision.allowed
    assert decision.required_capability == Capability.MAIL_SEND
