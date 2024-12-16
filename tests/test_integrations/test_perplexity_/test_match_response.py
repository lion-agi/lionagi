import pytest

from lionagi.integrations.perplexity_.api_endpoints.api_request import (
    PerplexityRequest,
)
from lionagi.integrations.perplexity_.api_endpoints.chat_completions.response.response_body import (
    PerplexityChatCompletionResponseBody,
)
from lionagi.integrations.perplexity_.api_endpoints.match_response import (
    match_response,
)


def test_match_chat_completion_response():
    request_model = PerplexityRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
    )

    response_data = {
        "id": "resp_123",
        "model": "llama-3.1-sonar-small-128k-online",
        "object": "chat.completion",
        "created": 1234567890,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        },
        "citations": [
            {
                "url": "https://example.com",
                "text": "Example text",
                "title": "Example Title",
            }
        ],
        "related_questions": [{"text": "What is the weather like?"}],
    }

    response = match_response(request_model, response_data)
    assert isinstance(response, PerplexityChatCompletionResponseBody)
    assert response.id == "resp_123"
    assert response.model == "llama-3.1-sonar-small-128k-online"
    assert response.object == "chat.completion"
    assert response.created == 1234567890
    assert len(response.choices) == 1
    assert response.choices[0].message.content == "Hello!"
    assert response.usage.total_tokens == 15
    assert len(response.citations) == 1
    assert len(response.related_questions) == 1


def test_match_empty_response():
    request_model = PerplexityRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
    )

    # Test with None
    response = match_response(request_model, None)
    assert response is None

    # Test with empty dict
    response = match_response(request_model, {})
    assert response == {}


def test_match_streaming_response():
    request_model = PerplexityRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
    )

    stream_chunks = [
        {"id": "1", "choices": [{"message": {"content": "Hello"}}]},
        {"id": "2", "choices": [{"message": {"content": "!"}}]},
    ]

    response = match_response(request_model, stream_chunks)
    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0]["id"] == "1"
    assert response[1]["id"] == "2"


def test_match_unknown_endpoint():
    request_model = PerplexityRequest(
        api_key="test_key",
        endpoint="unknown/endpoint",
        method="POST",
    )

    response_data = {"some": "data"}
    response = match_response(request_model, response_data)
    assert response == response_data
