"""Tests for service_match_util module."""

from unittest.mock import Mock

import pytest

from lionagi.service.service import Service, register_service
from lionagi.service.service_match_util import (
    match_parameters,
    match_service,
    match_task_method,
)


@register_service
class MockService(Service):
    def __init__(self, name=None):
        super().__init__()
        self.name = name or f"mock_{id(self)}"  # Unique name for each instance
        self.match_data_model = Mock(return_value={})

    def chat(self):
        pass

    def chat_completion(self):
        pass

    def text_completion(self):
        pass


def test_match_service_invalid():
    """Test matching invalid service."""
    with pytest.raises(
        ValueError, match="Service invalid_service is not available"
    ):
        match_service("invalid_service")


def test_match_service_reuse():
    """Test reusing existing service instance."""
    service1 = MockService()
    service2 = MockService()
    assert service1 is not service2  # Different instances


def test_match_task_method():
    """Test matching task method."""
    service = MockService()

    # Test exact match
    assert match_task_method("chat_completion", service) == ["chat_completion"]

    # Test partial match
    assert sorted(match_task_method("chat", service)) == [
        "chat",
        "chat_completion",
    ]

    # Test no match
    assert match_task_method("invalid", service) == []


def test_match_parameters():
    """Test matching parameters for a method."""

    def test_method(
        model=None, limit_tokens=None, limit_requests=None, extra=None
    ):
        pass

    # Test with all parameters
    params = match_parameters(
        test_method, model="gpt-4", interval_tokens=1000, interval_requests=10
    )
    assert params == {
        "model": "gpt-4",
        "limit_tokens": 1000,
        "limit_requests": 10,
    }


def test_match_parameters_with_warnings():
    """Test parameter matching warnings."""

    def test_method(model=None):
        pass

    # Should warn about unsupported parameters
    with pytest.warns(UserWarning) as record:
        match_parameters(
            test_method,
            model="gpt-4",
            interval_tokens=1000,
            interval_requests=10,
        )

    warnings = [str(w.message).lower() for w in record]
    assert any("limit tokens" in w or "limit requests" in w for w in warnings)


def test_match_task_method_case_insensitive():
    """Test case-insensitive task method matching."""
    service = MockService()
    assert sorted(match_task_method("CHAT", service)) == [
        "chat",
        "chat_completion",
    ]
    assert match_task_method("chat_COMPLETION", service) == ["chat_completion"]


def test_match_task_method_with_special_chars():
    """Test task method matching with special characters."""

    @register_service
    class TestService(Service):
        def __init__(self):
            super().__init__()
            self.name = f"test_{id(self)}"  # Unique name

        def chat_completion_v2(self):
            pass

    service = TestService()
    assert match_task_method("chat-completion", service) == [
        "chat_completion_v2"
    ]
    assert match_task_method("chat.completion", service) == [
        "chat_completion_v2"
    ]
