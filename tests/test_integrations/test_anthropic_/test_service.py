import pytest
from pydantic import ValidationError

from lionagi.integrations.anthropic_.AnthropicService import AnthropicService
from lionagi.service.rate_limiter import RateLimiter


def test_initialization():
    # Test basic initialization
    service = AnthropicService(api_key="test_key")
    assert service.api_key == "test_key"
    assert service.api_version == "2023-06-01"  # default version
    assert service.name is None
    assert isinstance(service.rate_limiters, dict)

    # Test with all parameters
    service = AnthropicService(
        api_key="test_key",
        api_version="2024-01-01",
        name="test_service",
    )
    assert service.api_version == "2024-01-01"
    assert service.name == "test_service"


def test_immutable_attributes():
    service = AnthropicService(api_key="test_key")

    # Test immutable api_key
    with pytest.raises(AttributeError):
        service.api_key = "new_key"

    # Test immutable api_version
    with pytest.raises(AttributeError):
        service.api_version = "2024-01-01"

    # Test mutable name
    service.name = "new_name"
    assert service.name == "new_name"


def test_check_rate_limiter():
    service = AnthropicService(api_key="test_key")

    # Test rate limiter creation for new model
    message_model = service.create_message(
        model="claude-2", limit_tokens=1000, limit_requests=100
    )
    assert "claude-2" in service.rate_limiters
    assert service.rate_limiters["claude-2"].limit_tokens == 1000
    assert service.rate_limiters["claude-2"].limit_requests == 100

    # Test rate limiter reuse for same model
    message_model2 = service.create_message(
        model="claude-2",
        limit_tokens=2000,
        limit_requests=200,  # Different limits
    )
    assert message_model2.rate_limiter is message_model.rate_limiter
    assert message_model2.rate_limiter.limit_tokens == 2000  # Updated limits
    assert message_model2.rate_limiter.limit_requests == 200


def test_shared_rate_limiters():
    service = AnthropicService(api_key="test_key")

    # Test shared rate limiters for model variants
    opus_model = service.create_message(
        model="claude-3-opus-20240229", limit_tokens=1000, limit_requests=100
    )
    assert "claude-3-opus" in service.rate_limiters
    assert opus_model.rate_limiter is service.rate_limiters["claude-3-opus"]

    sonnet_model = service.create_message(
        model="claude-3-sonnet-20240229", limit_tokens=1000, limit_requests=100
    )
    assert "claude-3-sonnet" in service.rate_limiters
    assert (
        sonnet_model.rate_limiter is service.rate_limiters["claude-3-sonnet"]
    )

    haiku_model = service.create_message(
        model="claude-3-haiku-20240307", limit_tokens=1000, limit_requests=100
    )
    assert "claude-3-haiku" in service.rate_limiters
    assert haiku_model.rate_limiter is service.rate_limiters["claude-3-haiku"]


def test_list_tasks():
    service = AnthropicService(api_key="test_key")
    tasks = service.list_tasks()

    # Verify core tasks are present
    assert "create_message" in tasks

    # Verify internal methods are excluded
    assert "__init__" not in tasks
    assert "__setattr__" not in tasks
    assert "check_rate_limiter" not in tasks


def test_message_creation():
    service = AnthropicService(api_key="test_key")

    # Test basic model creation
    model = service.create_message(model="claude-2")
    assert model.model == "claude-2"
    assert model.request_model.api_key == "test_key"
    assert model.request_model.endpoint == "messages"
    assert model.request_model.api_version == "2023-06-01"

    # Test with rate limits
    model = service.create_message(
        model="claude-2", limit_tokens=1000, limit_requests=100
    )
    assert model.rate_limiter.limit_tokens == 1000
    assert model.rate_limiter.limit_requests == 100

    # Test with custom API version
    service = AnthropicService(
        api_key="test_key",
        api_version="2024-01-01",
    )
    model = service.create_message(model="claude-2")
    assert model.request_model.api_version == "2024-01-01"


def test_model_version_mapping():
    service = AnthropicService(api_key="test_key")

    # Test rate limiter mapping for claude-3 models
    models = {
        "claude-3-opus-20240229": "claude-3-opus",
        "claude-3-sonnet-20240229": "claude-3-sonnet",
        "claude-3-haiku-20240307": "claude-3-haiku",
    }

    for model_version, base_model in models.items():
        model = service.create_message(
            model=model_version, limit_tokens=1000, limit_requests=100
        )
        assert base_model in service.rate_limiters
        assert model.rate_limiter is service.rate_limiters[base_model]

        # Create another instance with the same base model
        model2 = service.create_message(
            model=model_version, limit_tokens=2000, limit_requests=200
        )
        assert model2.rate_limiter is model.rate_limiter
        assert model2.rate_limiter.limit_tokens == 2000
        assert model2.rate_limiter.limit_requests == 200
