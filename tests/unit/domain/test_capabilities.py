from icloud_access_broker.domain import Capability, has_capability


def test_has_capability_allows_granted_capability() -> None:
    granted_capabilities = frozenset({Capability.CALENDAR_READ})

    assert has_capability(granted_capabilities, Capability.CALENDAR_READ)


def test_has_capability_denies_missing_capability() -> None:
    granted_capabilities = frozenset({Capability.MAIL_READ})

    assert not has_capability(granted_capabilities, Capability.MAIL_SEND)


def test_read_capability_does_not_imply_write_or_send() -> None:
    granted_capabilities = frozenset({Capability.CALENDAR_READ, Capability.MAIL_READ})

    assert not has_capability(granted_capabilities, Capability.CALENDAR_WRITE)
    assert not has_capability(granted_capabilities, Capability.MAIL_SEND)
