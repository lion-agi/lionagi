import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lionagi.integrations.perplexity_.api_endpoints.chat_completions.request.request_body import (
    Message,
    PerplexityChatCompletionRequestBody,
)
from lionagi.integrations.perplexity_.PerplexityService import (
    PerplexityService,
)


@pytest.mark.asyncio
async def test_perplexity_chat_completion():
    # Mock response data
    mock_response = {
        "id": "resp_123",
        "model": "llama-3.1-sonar-small-128k-online",
        "object": "chat.completion",
        "created": 1234567890,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "The current weather in San Diego is sunny with a temperature of 72°F.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 20,
            "completion_tokens": 15,
            "total_tokens": 35,
        },
        "citations": [
            {
                "url": "https://weather.com/san-diego",
                "text": "Current conditions in San Diego: 72°F and sunny",
                "title": "San Diego Weather",
            }
        ],
        "related_questions": [
            {"text": "What's the weather forecast for tomorrow in San Diego?"},
            {"text": "What's the average temperature in San Diego?"},
        ],
    }

    # Create service
    service = PerplexityService(api_key="test-key")

    # Create model
    model = service.create_chat_completion(
        model="llama-3.1-sonar-small-128k-online",
        limit_tokens=1000,
        limit_requests=100,
    )

    # Create request
    request = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[
            Message(
                role="system", content="You are a helpful weather assistant."
            ),
            Message(
                role="user", content="What's the weather like in San Diego?"
            ),
        ],
        temperature=0.7,
        return_related_questions=True,
    )

    # Mock the API call
    mock_invoke = AsyncMock(
        return_value=(mock_response, {"date": "Thu, 01 Jan 1970 00:00:00 GMT"})
    )
    with patch.object(model.request_model, "invoke", mock_invoke):
        # Make the request
        response = await model.invoke(request)

        # Verify response
        assert response.model == "llama-3.1-sonar-small-128k-online"
        assert len(response.choices) == 1
        assert "San Diego" in response.choices[0].message.content
        assert response.usage.total_tokens == 35
        assert len(response.citations) == 1
        assert len(response.related_questions) == 2


@pytest.mark.asyncio
async def test_perplexity_streaming():
    # Mock streaming response chunks
    mock_chunks = [
        {"id": "1", "choices": [{"message": {"content": "The "}}]},
        {"id": "2", "choices": [{"message": {"content": "current "}}]},
        {"id": "3", "choices": [{"message": {"content": "weather "}}]},
        {"id": "4", "choices": [{"message": {"content": "is "}}]},
        {"id": "5", "choices": [{"message": {"content": "sunny."}}]},
        {
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            }
        },
    ]

    # Create service and model
    service = PerplexityService(api_key="test-key")
    model = service.create_chat_completion(
        model="llama-3.1-sonar-small-128k-online",
        limit_tokens=1000,
        limit_requests=100,
    )

    # Create request with streaming enabled
    request = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[Message(role="user", content="What's the weather?")],
        stream=True,
    )

    # Mock the streaming API call
    async def mock_stream(*args, **kwargs):
        yield {"headers": {"date": "Thu, 01 Jan 1970 00:00:00 GMT"}}
        for chunk in mock_chunks:
            yield chunk

    with patch.object(model.request_model, "stream", mock_stream):
        # Make the streaming request
        response = await model.stream(request)

        # Verify response chunks
        assert len(response) == len(mock_chunks)
        content = "".join(
            chunk["choices"][0]["message"]["content"]
            for chunk in response[:-1]  # Exclude usage chunk
        )
        assert content == "The current weather is sunny."
        assert response[-1]["usage"]["total_tokens"] == 15


if __name__ == "__main__":
    pytest.main([__file__])
