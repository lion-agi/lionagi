import pytest
from pydantic import ValidationError

from lionagi.integrations.openai_.OpenAIService import OpenAIService
from lionagi.service.rate_limiter import RateLimiter


def test_immutable_attributes():
    service = OpenAIService(api_key="test_key")

    # Test immutable api_key
    with pytest.raises(AttributeError):
        service.api_key = "new_key"

    # Test immutable organization
    with pytest.raises(AttributeError):
        service.openai_organization = "new_org"

    # Test immutable project
    with pytest.raises(AttributeError):
        service.openai_project = "new_proj"

    # Test mutable name
    service.name = "new_name"
    assert service.name == "new_name"


def test_check_rate_limiter():
    service = OpenAIService(api_key="test_key")

    # Test rate limiter creation for new model
    chat_model = service.create_chat_completion(
        model="gpt-4", limit_tokens=1000, limit_requests=100
    )
    assert "gpt-4" in service.rate_limiters
    assert service.rate_limiters["gpt-4"].limit_tokens == 1000
    assert service.rate_limiters["gpt-4"].limit_requests == 100

    # Test rate limiter reuse for same model
    chat_model2 = service.create_chat_completion(
        model="gpt-4",
        limit_tokens=2000,
        limit_requests=200,  # Different limits
    )
    assert chat_model2.rate_limiter is chat_model.rate_limiter
    assert chat_model2.rate_limiter.limit_tokens == 2000  # Updated limits
    assert chat_model2.rate_limiter.limit_requests == 200

    # Test shared rate limiters for model variants
    turbo_model = service.create_chat_completion(
        model="gpt-4-turbo-preview", limit_tokens=1000, limit_requests=100
    )
    assert "gpt-4-turbo" in service.rate_limiters
    assert turbo_model.rate_limiter is service.rate_limiters["gpt-4-turbo"]


def test_list_tasks():
    service = OpenAIService(api_key="test_key")
    tasks = service.list_tasks()

    # Verify core tasks are present
    assert "create_chat_completion" in tasks
    assert "create_embeddings" in tasks
    assert "create_image" in tasks
    assert "create_moderation" in tasks

    # Verify internal methods are excluded
    assert "__init__" not in tasks
    assert "check_rate_limiter" not in tasks
    assert "match_data_model" not in tasks


def test_chat_completion_creation():
    service = OpenAIService(api_key="test_key")

    # Test basic model creation
    model = service.create_chat_completion(model="gpt-4")
    assert model.model == "gpt-4"
    assert model.request_model.api_key == "test_key"
    assert model.request_model.endpoint == "chat/completions"

    # Test with rate limits
    model = service.create_chat_completion(
        model="gpt-4", limit_tokens=1000, limit_requests=100
    )
    assert model.rate_limiter.limit_tokens == 1000
    assert model.rate_limiter.limit_requests == 100

    # Test with organization and project
    service = OpenAIService(
        api_key="test_key",
        openai_organization="org-123",
        openai_project="proj-123",
    )
    model = service.create_chat_completion(model="gpt-4")
    assert model.request_model.openai_organization == "org-123"
    assert model.request_model.openai_project == "proj-123"


def test_embeddings_creation():
    service = OpenAIService(api_key="test_key")

    # Test basic model creation
    model = service.create_embeddings(model="text-embedding-ada-002")
    assert model.model == "text-embedding-ada-002"
    assert model.request_model.endpoint == "embeddings"

    # Test with rate limits
    model = service.create_embeddings(
        model="text-embedding-ada-002", limit_tokens=1000, limit_requests=100
    )
    assert model.rate_limiter.limit_tokens == 1000
    assert model.rate_limiter.limit_requests == 100


def test_speech_creation():
    service = OpenAIService(api_key="test_key")

    # Test basic model creation
    model = service.create_speech(model="tts-1")
    assert model.model == "tts-1"
    assert model.request_model.endpoint == "audio/speech"

    # Test with request limit
    model = service.create_speech(model="tts-1", limit_requests=100)
    assert model.rate_limiter.limit_requests == 100
    assert (
        model.rate_limiter.limit_tokens is None
    )  # Speech doesn't use token limits


def test_transcription_creation():
    service = OpenAIService(api_key="test_key")

    # Test basic model creation
    model = service.create_transcription(model="whisper-1")
    assert model.model == "whisper-1"
    assert model.request_model.endpoint == "audio/transcriptions"

    # Test with request limit
    model = service.create_transcription(model="whisper-1", limit_requests=100)
    assert model.rate_limiter.limit_requests == 100


def test_translation_creation():
    service = OpenAIService(api_key="test_key")

    # Test basic model creation
    model = service.create_translation(model="whisper-1")
    assert model.model == "whisper-1"
    assert model.request_model.endpoint == "audio/translations"

    # Test with request limit
    model = service.create_translation(model="whisper-1", limit_requests=100)
    assert model.rate_limiter.limit_requests == 100


def test_moderation_creation():
    service = OpenAIService(api_key="test_key")

    # Test basic request creation
    request = service.create_moderation()
    assert request.endpoint == "moderations"
    assert request.method == "POST"
    assert request.content_type == "application/json"
