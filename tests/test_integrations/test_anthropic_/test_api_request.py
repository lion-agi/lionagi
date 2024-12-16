import json
import os
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import aiohttp
import pytest
from pydantic import BaseModel

from lionagi.integrations.anthropic_.api_endpoints.api_request import (
    AnthropicRequest,
)
from lionagi.integrations.anthropic_.api_endpoints.data_models import (
    AnthropicEndpointPathParam,
)
from lionagi.integrations.anthropic_.api_endpoints.messages.request.message_models import (
    Message,
)
from lionagi.integrations.anthropic_.api_endpoints.messages.request.request_body import (
    AnthropicMessageRequestBody,
)


class MockResponse:
    def __init__(self, status, json_data, headers=None):
        self.status = status
        self._json_data = json_data
        self.headers = headers or {}
        self.request_info = MagicMock()
        self.request_info.real_url = "https://api.anthropic.com/v1/messages"
        self.history = None
        self._content = json.dumps(json_data).encode()

    async def json(self):
        return self._json_data

    async def text(self):
        if isinstance(self._json_data, str):
            return self._json_data
        return json.dumps(self._json_data)

    async def read(self):
        return self._content

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
    return AnthropicRequest(
        api_key="test_key",
        endpoint="messages",
        method="POST",
        content_type="application/json",
    )


def test_initialization():
    # Test basic initialization
    request = AnthropicRequest(
        api_key="test_key",
        endpoint="messages",
        method="POST",
    )
    assert request.api_key == "test_key"
    assert request.endpoint == "messages"
    assert request.method == "POST"
    assert request.api_version == "2023-06-01"  # default version

    # Test with custom API version
    request = AnthropicRequest(
        api_key="test_key",
        endpoint="messages",
        method="POST",
        api_version="2024-01-01",
    )
    assert request.api_version == "2024-01-01"


def test_api_key_validation():
    # Test with environment variable
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env_test_key"}):
        request = AnthropicRequest(
            api_key="ANTHROPIC_API_KEY",
            endpoint="messages",
            method="POST",
        )
        assert request.api_key == "env_test_key"

    # Test with direct key
    request = AnthropicRequest(
        api_key="direct_test_key",
        endpoint="messages",
        method="POST",
    )
    assert request.api_key == "direct_test_key"


@pytest.mark.asyncio
async def test_invoke_error(api_request):
    error_response = {
        "error": {
            "type": "authentication_error",
            "message": "Invalid API key",
        }
    }

    request_body = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[Message(role="user", content="Hi")],
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
            "type": "message_start",
            "message": {
                "id": "msg_123",
                "type": "message",
                "role": "assistant",
                "model": "claude-3-sonnet",
                "content": [],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 49, "output_tokens": 4},
            },
        },
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "text", "text": ""},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "Hello"},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "!"},
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn", "stop_sequence": None},
            "usage": {"output_tokens": 10},
        },
        {"type": "message_stop"},
    ]

    request_body = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[Message(role="user", content="Hi")],
        stream=True,
    )

    mock_response = MockResponse(200, chunks)
    mock_response.content = MockAsyncIterator(
        [f"data: {json.dumps(chunk)}\n\n".encode() for chunk in chunks]
        + [b"data: [DONE]\n\n"]
    )

    with patch(
        "aiohttp.ClientSession.request",
        return_value=mock_response,
    ) as mock_request:
        with patch("builtins.print") as mock_print:
            response_chunks = []
            async for chunk in api_request.stream(json_data=request_body):
                response_chunks.append(chunk)

            # Verify print calls
            mock_print.assert_any_call("Hello", end="", flush=True)
            mock_print.assert_any_call("!", end="", flush=True)

        # Verify raw chunks are returned
        assert len(response_chunks) == len(chunks)
        assert response_chunks[0]["type"] == "message_start"
        assert response_chunks[2]["type"] == "content_block_delta"
        assert response_chunks[2]["delta"]["type"] == "text_delta"
        assert response_chunks[2]["delta"]["text"] == "Hello"
        assert response_chunks[-1]["type"] == "message_stop"

        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_stream_with_file_output(api_request, tmp_path):
    chunks = [
        {
            "type": "message_start",
            "message": {
                "id": "msg_123",
                "type": "message",
                "role": "assistant",
                "model": "claude-3-sonnet",
                "content": [],
            },
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "Hello"},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "!"},
        },
        {"type": "message_stop"},
    ]

    output_file = tmp_path / "stream.jsonl"

    mock_response = MockResponse(200, chunks)
    mock_response.content = MockAsyncIterator(
        [f"data: {json.dumps(chunk)}\n\n".encode() for chunk in chunks]
        + [b"data: [DONE]\n\n"]
    )

    with patch(
        "aiohttp.ClientSession.request",
        return_value=mock_response,
    ):
        request_body = AnthropicMessageRequestBody(
            model="claude-2",
            messages=[Message(role="user", content="Hi")],
            stream=True,
        )
        response_chunks = []
        async for chunk in api_request.stream(
            json_data=request_body,
            output_file=str(output_file),
        ):
            response_chunks.append(chunk)

        assert output_file.exists()
        with open(output_file) as f:
            lines = f.readlines()
            assert len(lines) == len(chunks)
            assert "Hello" in lines[1]
            assert "!" in lines[2]


@pytest.mark.asyncio
async def test_stream_without_stream_flag(api_request):
    request_body = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[Message(role="user", content="Hi")],
        stream=False,
    )

    with pytest.raises(ValueError, match="Request does not support stream"):
        async for _ in api_request.stream(json_data=request_body):
            pass
