from dataclasses import dataclass
from typing import Any

from icloud_access_broker.adapters.input.cli import run
from icloud_access_broker.application.dtos import ServiceInfo


@dataclass(frozen=True, slots=True)
class StubServiceInfoProvider:
    service_info: ServiceInfo

    def execute(self) -> ServiceInfo:
        return self.service_info


def test_prints_installed_message(capsys: Any) -> None:
    exit_code = run([], StubServiceInfoProvider(ServiceInfo("Example Broker", "example-broker", "example_broker")))

    assert exit_code == 0
    assert capsys.readouterr().out == "Example Broker is installed.\n"


def test_prints_version_metadata(capsys: Any) -> None:
    exit_code = run(
        ["--version"], StubServiceInfoProvider(ServiceInfo("Example Broker", "example-broker", "example_broker"))
    )

    assert exit_code == 0
    assert capsys.readouterr().out == "Example Broker (example-broker)\n"
