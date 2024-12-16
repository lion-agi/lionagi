import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from pydantic import BaseModel

from lionagi.integrations.openai_.api_endpoints.api_request import (
    OpenAIRequest,
)
from lionagi.integrations.openai_.api_endpoints.chat_completions.request.message_models import (
    UserMessage,
)
from lionagi.integrations.openai_.api_endpoints.chat_completions.request.request_body import (
    OpenAIChatCompletionRequestBody,
)


class MockResponse:
    def __init__(self, status, json_data, headers=None):
        self.status = status
        self._json_data = json_data
        self.headers = headers or {}
        self.request_info = MagicMock()
        self.request_info.real_url = (
            "https://api.openai.com/v1/chat/completions"
        )
        self.history = None

    async def json(self):
        return self._json_data

    async def text(self):
        if isinstance(self._json_data, str):
            return self._json_data
        return json.dumps(self._json_data)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockAsyncIterator:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.data):
            raise StopAsyncIteration
        result = self.data[self.index]
        self.index += 1
        return result


@pytest.fixture
def api_request():
    return OpenAIRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
        content_type="application/json",
    )


def test_initialization():
    # Test basic initialization
    request = OpenAIRequest(
        api_key="test_key", endpoint="chat/completions", method="POST"
    )
    assert request.api_key == "test_key"
    assert request.endpoint == "chat/completions"
    assert request.method == "POST"

    # Test with organization
    request = OpenAIRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
        openai_organization="org-123",
    )
    assert request.openai_organization == "org-123"

    # Test with project
    request = OpenAIRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
        openai_project="proj-123",
    )
    assert request.openai_project == "proj-123"


@pytest.mark.asyncio
async def test_invoke_error(api_request):
    error_response = {
        "error": {
            "message": "Invalid API key",
            "type": "invalid_request_error",
            "code": "invalid_api_key",
        }
    }

    request_body = OpenAIChatCompletionRequestBody(
        model="gpt-4", messages=[UserMessage(role="user", content="Hi")]
    )

    with patch(
        "aiohttp.ClientSession.request",
        return_value=MockResponse(401, error_response),
    ) as mock_request:
        with pytest.raises(aiohttp.ClientResponseError) as exc_info:
            await api_request.invoke(json_data=request_body)

        assert "Invalid API key" in str(exc_info.value)
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_stream(api_request):
    chunks = [
        {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "delta": {"role": "assistant", "content": "Hello"},
                    "index": 0,
                    "finish_reason": None,
                    "logprobs": None,
                }
            ],
            "created": 1677858242,
            "model": "gpt-4",
            "object": "chat.completion.chunk",
        },
        {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "delta": {"content": "!"},
                    "index": 0,
                    "finish_reason": "stop",
                    "logprobs": None,
                }
            ],
            "created": 1677858242,
            "model": "gpt-4",
            "object": "chat.completion.chunk",
        },
    ]

    request_body = OpenAIChatCompletionRequestBody(
        model="gpt-4",
        messages=[UserMessage(role="user", content="Hi")],
        stream=True,
    )

    mock_response = MockResponse(200, chunks)
    mock_response.content = MockAsyncIterator(
        [f"data: {json.dumps(chunk)}\n\n".encode() for chunk in chunks]
        + [b"data: [DONE]\n\n"]
    )

    with patch(
        "aiohttp.ClientSession.request", return_value=mock_response
    ) as mock_request:
        responses = []
        async for chunk in api_request.stream(json_data=request_body):
            responses.append(chunk)

        assert len(responses) == 2
        assert responses[0]["choices"][0]["delta"]["content"] == "Hello"
        assert responses[1]["choices"][0]["delta"]["content"] == "!"
        mock_request.assert_called_once()


def test_base_url(api_request):
    assert api_request.base_url == "https://api.openai.com/v1/"


def test_get_endpoint(api_request):
    # Test without path params
    assert api_request.get_endpoint() == "chat/completions"

    # Test with path params
    class PathParams(BaseModel):
        model_id: str

    params = PathParams(model_id="gpt-4")
    api_request.endpoint = "models/{model_id}"
    assert api_request.get_endpoint(params) == "models/gpt-4"
