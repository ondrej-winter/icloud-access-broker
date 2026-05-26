from icloud_access_broker.application.use_cases import GetServiceInfo


def test_returns_service_metadata() -> None:
    service_info = GetServiceInfo().execute()

    assert service_info.name == "iCloud Access Broker"
    assert service_info.package_name == "icloud-access-broker"
    assert service_info.import_name == "icloud_access_broker"
