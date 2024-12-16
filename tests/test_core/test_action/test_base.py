from typing import Any

import pytest

from lionagi.core.action.base import EventStatus, ObservableAction
from lionagi.core.generic import Log
from lionagi.core.typing import UNDEFINED
from lionagi.settings import TimedFuncCallConfig


@pytest.fixture
def test_action():
    """Fixture for creating a test action."""

    class TestAction(ObservableAction):
        """Test implementation of ObservableAction."""

        def __init__(self, timed_config=None, **kwargs):
            super().__init__(timed_config=timed_config, **kwargs)

    return TestAction


def test_event_status_values():
    """Test EventStatus enum values."""
    assert EventStatus.PENDING == "pending"
    assert EventStatus.PROCESSING == "processing"
    assert EventStatus.COMPLETED == "completed"
    assert EventStatus.FAILED == "failed"


def test_observable_action_init(test_action):
    """Test ObservableAction initialization."""
    # Test default initialization
    action = test_action()
    assert action.status == EventStatus.PENDING
    assert action.execution_time is None
    assert action.execution_response is None
    assert action.execution_error is None
    assert action._timed_config is not None  # Should use default config

    # Test with custom timed_config
    config = TimedFuncCallConfig(
        initial_delay=1,
        retry_default=UNDEFINED,
        retry_timeout=5,
        retry_timing=True,
    )
    action = test_action(timed_config=config)
    assert action._timed_config == config

    # Test with config as dict
    config_dict = {
        "initial_delay": 1,
        "retry_default": UNDEFINED,
        "retry_timeout": 5,
        "retry_timing": True,
    }
    action = test_action(timed_config=config_dict)
    assert action._timed_config.initial_delay == 1
    assert action._timed_config.retry_timeout == 5


def test_observable_action_to_log(test_action):
    """Test ObservableAction log conversion."""
    action = test_action()
    action.execution_response = "test_response"

    log = action.to_log()
    assert isinstance(log, Log)
    assert log.content["execution_response"] == "test_response"
    assert log.loginfo["status"] == EventStatus.PENDING


def test_observable_action_from_dict():
    """Test ObservableAction from_dict raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        ObservableAction.from_dict({})


def test_observable_action_with_config_kwargs(test_action):
    """Test ObservableAction with kwargs in timed_config."""
    config = TimedFuncCallConfig(
        initial_delay=1,
        retry_default=UNDEFINED,
        retry_timeout=5,
        retry_timing=True,
    )
    action = test_action(timed_config=config)
    assert action._timed_config.initial_delay == 1
    assert action._timed_config.retry_timeout == 5
    assert action._timed_config.retry_timing is True
