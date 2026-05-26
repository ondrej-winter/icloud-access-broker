from icloud_access_broker.application.dtos import ServiceInfo


class GetServiceInfo:
    """Return static service metadata for adapters that need a health-style response."""

    def execute(self) -> ServiceInfo:
        return ServiceInfo(
            name="iCloud Access Broker",
            package_name="icloud-access-broker",
            import_name="icloud_access_broker",
        )
