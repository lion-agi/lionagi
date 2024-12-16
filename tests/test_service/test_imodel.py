"""Tests for imodel module."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import BaseModel

from lionagi.service.imodel import iModel
from lionagi.service.service import Service


class MockDataModel(BaseModel):
    model: str = None


class MockRequestModel:
    def __init__(self):
        self.invoke = AsyncMock(return_value="response")


class MockService(Service):
    def __init__(self, name=None):
        super().__init__()
        self.name = name or f"mock_{id(self)}"  # Unique name for each instance
        self.match_data_model = Mock(return_value={"request": MockDataModel})
        self._request_model = MockRequestModel()

    def chat(self):
        return self._request_model

    def list_tasks(self):
        return ["chat", "completion"]


def test_imodel_initialization():
    """Test iModel initialization with different parameters."""
    service = MockService()

    model = iModel(
        provider=service, task="chat", model="gpt-4", api_key="test_key"
    )

    assert model.service == service
    assert model.task == "chat"
    assert model.model == "gpt-4"


def test_imodel_initialization_with_string_provider():
    """Test iModel initialization with provider name."""
    with patch("lionagi.service.imodel.match_service") as mock_match:
        mock_service = MockService()
        mock_match.return_value = mock_service

        model = iModel(
            provider="mock_provider",
            task="chat",
            model="gpt-4",
            api_key="test_key",
        )

        assert model.service == mock_service
        assert model.task == "chat"
        assert model.model == "gpt-4"
        mock_match.assert_called_once_with("mock_provider", api_key="test_key")


def test_imodel_with_invalid_provider():
    """Test iModel initialization with invalid provider."""
    with pytest.raises(ValueError, match="Invalid provider"):
        iModel(provider=123)


def test_imodel_with_invalid_task():
    """Test iModel initialization with invalid task."""
    service = MockService()

    with pytest.raises(ValueError, match="No matching task found"):
        iModel(provider=service, task="invalid_task")


def test_imodel_with_ambiguous_task():
    """Test iModel initialization with ambiguous task."""

    class AmbiguousService(MockService):
        def chat_completion(self):
            return self._request_model

        def chat_summary(self):
            return self._request_model

        def list_tasks(self):
            return ["chat_completion", "chat_summary"]

    service = AmbiguousService()

    with pytest.raises(ValueError, match="Multiple possible tasks found"):
        iModel(provider=service, task="chat")


def test_parse_to_data_model():
    """Test parsing parameters to data model."""
    service = MockService()

    model = iModel(provider=service, task="chat", model="gpt-4")

    parsed = model.parse_to_data_model(temperature=0.7)
    assert isinstance(parsed["request"], MockDataModel)
    assert parsed["request"].model == "gpt-4"


def test_parse_to_data_model_with_inconsistent_model():
    """Test parsing with inconsistent model parameter."""
    service = MockService()

    model = iModel(provider=service, task="chat", model="gpt-4")

    with pytest.raises(ValueError, match="Models are inconsistent"):
        model.parse_to_data_model(model="gpt-3.5-turbo")


@pytest.mark.asyncio
async def test_invoke():
    """Test invoke method."""
    service = MockService()

    model = iModel(provider=service, task="chat", model="gpt-4")

    result = await model.invoke(
        messages=[{"role": "user", "content": "Hello"}]
    )
    assert result == "response"
    model.request_model.invoke.assert_called_once_with(
        messages=[{"role": "user", "content": "Hello"}]
    )


def test_list_tasks():
    """Test list_tasks method."""
    service = MockService()

    model = iModel(provider=service, task="chat", model="gpt-4")

    tasks = model.list_tasks()
    assert tasks == ["chat", "completion"]


def test_imodel_with_deprecated_parameters():
    """Test handling of deprecated parameters."""
    service = MockService()

    with pytest.warns(DeprecationWarning):
        model = iModel(
            provider=service,
            task="chat",
            model="gpt-4",
            config={"deprecated": True},
        )

    with pytest.warns(DeprecationWarning):
        model = iModel(
            provider=service,
            task="chat",
            model="gpt-4",
            provider_schema={"deprecated": True},
        )

    with pytest.warns(DeprecationWarning):
        model = iModel(
            provider=service,
            task="chat",
            model="gpt-4",
            endpoint="chat",  # Use valid task to avoid ValueError
        )


def test_imodel_with_api_key_schema():
    """Test initialization with api_key_schema."""
    with patch("lionagi.service.imodel.match_service") as mock_match:
        mock_service = MockService()
        mock_match.return_value = mock_service

        model = iModel(
            provider="mock_provider",
            task="chat",
            model="gpt-4",
            api_key_schema="test_key",
        )

        mock_match.assert_called_once_with("mock_provider", api_key="test_key")


def test_imodel_with_rate_limits():
    """Test initialization with rate limits."""
    service = MockService()

    model = iModel(
        provider=service,
        task="chat",
        model="gpt-4",
        interval_tokens=1000,
        interval_requests=10,
    )

    assert model.request_model is not None


def test_imodel_with_additional_kwargs():
    """Test initialization with additional kwargs."""
    service = MockService()

    model = iModel(
        provider=service, task="chat", model="gpt-4", custom_param="value"
    )

    assert model.configs["custom_param"] == "value"


def test_imodel_with_service_instance_and_api_key():
    """Test initialization with both service instance and api_key."""
    service = MockService()

    with pytest.warns(
        UserWarning,
        match="A Service instance was provided along with api key info",
    ):
        model = iModel(
            provider=service, task="chat", model="gpt-4", api_key="test_key"
        )
