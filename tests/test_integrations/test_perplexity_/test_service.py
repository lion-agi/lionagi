import pytest
from pydantic import ValidationError

from lionagi.integrations.perplexity_.api_endpoints.chat_completions.request.request_body import (
    PerplexityChatCompletionRequestBody,
)
from lionagi.integrations.perplexity_.PerplexityService import (
    PerplexityService,
)
from lionagi.service.rate_limiter import RateLimiter


def test_immutable_attributes():
    service = PerplexityService(api_key="test_key")

    # Test immutable api_key
    with pytest.raises(AttributeError):
        service.api_key = "new_key"

    # Test mutable name
    service.name = "new_name"
    assert service.name == "new_name"


def test_check_rate_limiter():
    service = PerplexityService(api_key="test_key")

    # Test rate limiter creation for new model
    chat_model = service.create_chat_completion(
        model="llama-3.1-sonar-small-128k-online",
        limit_tokens=1000,
        limit_requests=100,
    )
    assert "llama-3.1-sonar-small" in service.rate_limiters
    assert service.rate_limiters["llama-3.1-sonar-small"].limit_tokens == 1000
    assert service.rate_limiters["llama-3.1-sonar-small"].limit_requests == 100

    # Test rate limiter reuse for same model
    chat_model2 = service.create_chat_completion(
        model="llama-3.1-sonar-small-128k-online",
        limit_tokens=2000,
        limit_requests=200,  # Different limits
    )
    assert chat_model2.rate_limiter is chat_model.rate_limiter
    assert chat_model2.rate_limiter.limit_tokens == 2000  # Updated limits
    assert chat_model2.rate_limiter.limit_requests == 200


def test_shared_rate_limiters():
    service = PerplexityService(api_key="test_key")

    # Test shared rate limiters for model variants
    models = {
        "llama-3.1-sonar-small-128k-online": "llama-3.1-sonar-small",
        "llama-3.1-sonar-medium-128k-online": "llama-3.1-sonar-medium",
        "llama-3.1-sonar-large-128k-online": "llama-3.1-sonar-large",
    }

    for model_version, base_model in models.items():
        model = service.create_chat_completion(
            model=model_version, limit_tokens=1000, limit_requests=100
        )
        assert base_model in service.rate_limiters
        assert model.rate_limiter is service.rate_limiters[base_model]

        # Create another instance with the same base model
        model2 = service.create_chat_completion(
            model=model_version, limit_tokens=2000, limit_requests=200
        )
        assert model2.rate_limiter is model.rate_limiter
        assert model2.rate_limiter.limit_tokens == 2000
        assert model2.rate_limiter.limit_requests == 200


def test_list_tasks():
    service = PerplexityService(api_key="test_key")
    tasks = service.list_tasks()

    # Verify core tasks are present
    assert "create_chat_completion" in tasks

    # Verify internal methods are excluded
    assert "__init__" not in tasks
    assert "__setattr__" not in tasks
    assert "check_rate_limiter" not in tasks
    assert "match_data_model" not in tasks


def test_chat_completion_creation():
    service = PerplexityService(api_key="test_key")

    # Test basic model creation
    model = service.create_chat_completion(
        model="llama-3.1-sonar-small-128k-online"
    )
    assert model.model == "llama-3.1-sonar-small-128k-online"
    assert model.request_model.api_key == "test_key"
    assert model.request_model.endpoint == "chat/completions"
    assert model.request_model.method == "POST"
    assert model.request_model.content_type == "application/json"

    # Test with rate limits
    model = service.create_chat_completion(
        model="llama-3.1-sonar-small-128k-online",
        limit_tokens=1000,
        limit_requests=100,
    )
    assert model.rate_limiter.limit_tokens == 1000
    assert model.rate_limiter.limit_requests == 100


def test_match_data_model():
    service = PerplexityService(api_key="test_key")

    # Test valid task
    models = service.match_data_model("create_chat_completion")
    assert models["request_body"] == PerplexityChatCompletionRequestBody

    # Test invalid task
    with pytest.raises(ValueError):
        service.match_data_model("invalid_task")
