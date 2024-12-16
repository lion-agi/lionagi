"""Tests for service module."""

import pytest

from lionagi.service.service import Service, ServiceSetting, register_service


def test_base_service():
    """Test base Service class."""
    service = Service()
    assert service.list_tasks() is None


def test_service_setting_singleton():
    """Test ServiceSetting is a singleton."""
    setting1 = ServiceSetting()
    setting2 = ServiceSetting()
    assert setting1 is setting2
    assert setting1.services == setting2.services


def test_register_multiple_services():
    """Test registering multiple services."""

    @register_service
    class Service1(Service):
        def __init__(self, name="service1"):
            super().__init__()
            self.name = name

    @register_service
    class Service2(Service):
        def __init__(self, name="service2"):
            super().__init__()
            self.name = name

    service1 = Service1()
    service2 = Service2()
    setting = ServiceSetting()

    assert "service1" in setting.services
    assert "service2" in setting.services
    assert setting.services["service1"] is service1
    assert setting.services["service2"] is service2


def test_duplicate_service_name():
    """Test registering service with duplicate name."""

    @register_service
    class Service1(Service):
        def __init__(self, name="duplicate"):
            super().__init__()
            self.name = name

    service1 = Service1()

    with pytest.raises(
        ValueError, match="Invalid name. There is a service using the name"
    ):

        @register_service
        class Service2(Service):
            def __init__(self, name="duplicate"):
                super().__init__()
                self.name = name

        service2 = Service2()


def test_service_without_name():
    """Test registering service without explicit name."""

    @register_service
    class TestService(Service):
        def __init__(self):
            super().__init__()
            self.name = None

    service = TestService()
    setting = ServiceSetting()

    # Should use auto-generated name
    found = False
    for name, registered_service in setting.services.items():
        if registered_service is service:
            assert name.startswith("TestService_")
            found = True
            break

    assert found, "Service not found in registry"


def test_add_service_manually():
    """Test adding service manually through ServiceSetting."""

    class TestService(Service):
        def __init__(self, name="test"):
            super().__init__()
            self.name = name

    service = TestService()
    setting = ServiceSetting()
    setting.add_service(service, "manual_test")

    assert "manual_test" in setting.services
    assert setting.services["manual_test"] is service


def test_add_service_without_name():
    """Test adding service without name."""

    class TestService(Service):
        def __init__(self):
            super().__init__()
            self.name = None

    service = TestService()
    setting = ServiceSetting()
    setting.add_service(service)

    # Should use auto-generated name
    found = False
    for name, registered_service in setting.services.items():
        if registered_service is service:
            assert name.startswith("TestService_")
            found = True
            break

    assert found, "Service not found in registry"


def test_service_setting_clear():
    """Test clearing ServiceSetting services."""

    @register_service
    class TestService(Service):
        def __init__(self, name="test"):
            super().__init__()
            self.name = name

    service = TestService()
    setting = ServiceSetting()

    # Clear services
    setting.services.clear()
    assert len(setting.services) == 0


def test_list_tasks_override():
    """Test overriding list_tasks in Service subclass."""

    @register_service
    class TestService(Service):
        def __init__(self, name="test"):
            super().__init__()
            self.name = name

        def list_tasks(self):
            return ["task1", "task2"]

    service = TestService()
    assert service.list_tasks() == ["task1", "task2"]
