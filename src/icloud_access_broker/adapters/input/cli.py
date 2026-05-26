from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from icloud_access_broker.application.use_cases import GetServiceInfo

if TYPE_CHECKING:
    from collections.abc import Sequence

    from icloud_access_broker.application.ports import ServiceInfoProvider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="icloud-access-broker", description="iCloud Access Broker CLI")
    parser.add_argument("--version", action="store_true", help="show service metadata and exit")
    return parser


def run(argv: Sequence[str] | None = None, service_info_provider: ServiceInfoProvider | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    provider = service_info_provider or GetServiceInfo()
    service_info = provider.execute()

    if args.version:
        print(f"{service_info.name} ({service_info.package_name})")
        return 0

    print(f"{service_info.name} is installed.")
    return 0


def main() -> int:
    return run()
