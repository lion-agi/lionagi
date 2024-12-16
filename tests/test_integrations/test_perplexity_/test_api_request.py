import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from lionagi.integrations.perplexity_.api_endpoints.api_request import (
    PerplexityRequest,
)
from lionagi.integrations.perplexity_.api_endpoints.chat_completions.request.request_body import (
    Message,
    PerplexityChatCompletionRequestBody,
)


@pytest.fixture
def mock_response():
    mock = AsyncMock()
    mock.status = 200
    mock.headers = {"Date": "Thu, 01 Jan 1970 00:00:00 GMT"}
    return mock


@pytest.fixture
def mock_session():
    with patch("aiohttp.ClientSession") as mock:
        yield mock


def test_initialization():
    request = PerplexityRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
    )
    assert request.api_key == "test_key"
    assert request.endpoint == "chat/completions"
    assert request.method == "POST"
    assert request.content_type == "application/json"
    assert request.base_url == "https://api.perplexity.ai"


@pytest.mark.asyncio
async def test_invoke_success(mock_session, mock_response):
    request = PerplexityRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
    )

    response_data = {
        "id": "resp_123",
        "choices": [{"message": {"content": "Hello!"}}],
    }
    mock_response.json = AsyncMock(return_value=response_data)
    mock_response.text = AsyncMock(return_value=json.dumps(response_data))

    # Create a mock for the request coroutine
    request_coro = AsyncMock(return_value=mock_response)
    mock_session.return_value.__aenter__.return_value.request = request_coro

    request_body = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[Message(role="user", content="Hi")],
    )

    # Test with parse_response=True
    response = await request.invoke(json_data=request_body)
    assert response == response_data

    # Test with parse_response=False
    response = await request.invoke(
        json_data=request_body, parse_response=False
    )
    assert response == response_data

    # Test with response headers
    response, headers = await request.invoke(
        json_data=request_body, with_response_header=True
    )
    assert response == response_data
    assert headers == {"date": "Thu, 01 Jan 1970 00:00:00 GMT"}


@pytest.mark.asyncio
async def test_invoke_error(mock_session, mock_response):
    request = PerplexityRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
    )

    mock_response.status = 400
    error_data = {"error": {"message": "Bad request"}}
    mock_response.json = AsyncMock(return_value=error_data)
    mock_response.text = AsyncMock(return_value=json.dumps(error_data))

    # Create a mock for the request coroutine
    request_coro = AsyncMock(return_value=mock_response)
    mock_session.return_value.__aenter__.return_value.request = request_coro

    request_body = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[Message(role="user", content="Hi")],
    )

    with pytest.raises(
        Exception, match="API request failed with status 400: Bad request"
    ):
        await request.invoke(json_data=request_body)


@pytest.mark.asyncio
async def test_stream_success(mock_session, mock_response):
    request = PerplexityRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
    )

    chunks = [
        b'data: {"id":"1","choices":[{"delta":{"content":"Hello"}}]}\n\n',
        b'data: {"id":"2","choices":[{"delta":{"content":"!"}}]}\n\n',
    ]

    class MockAsyncIterator:
        def __init__(self, chunks):
            self.chunks = chunks
            self.index = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.index >= len(self.chunks):
                raise StopAsyncIteration
            chunk = self.chunks[self.index]
            self.index += 1
            return chunk

    mock_response.content = MockAsyncIterator(chunks)
    mock_response.status = 200

    # Create a mock for the post coroutine
    post_coro = AsyncMock(return_value=mock_response)
    mock_session.return_value.__aenter__.return_value.post = post_coro

    request_body = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[Message(role="user", content="Hi")],
        stream=True,
    )

    chunks = []
    async for chunk in request.stream(json_data=request_body):
        chunks.append(chunk)

    assert len(chunks) == 2
    assert chunks[0]["id"] == "1"
    assert chunks[1]["id"] == "2"


@pytest.mark.asyncio
async def test_stream_error(mock_session, mock_response):
    request = PerplexityRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
    )

    mock_response.status = 400
    error_data = {"error": {"message": "Bad request"}}
    mock_response.json = AsyncMock(return_value=error_data)

    # Create a mock for the post coroutine
    post_coro = AsyncMock(return_value=mock_response)
    mock_session.return_value.__aenter__.return_value.post = post_coro

    request_body = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[Message(role="user", content="Hi")],
        stream=True,
    )

    with pytest.raises(
        Exception, match="API request failed with status 400: Bad request"
    ):
        async for _ in request.stream(json_data=request_body):
            pass


@pytest.mark.asyncio
async def test_file_output(mock_session, mock_response, tmp_path):
    request = PerplexityRequest(
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
    )

    chunks = [b"test data"]

    class MockAsyncIterator:
        def __init__(self, chunks):
            self.chunks = chunks
            self.index = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.index >= len(self.chunks):
                raise StopAsyncIteration
            chunk = self.chunks[self.index]
            self.index += 1
            return chunk

    mock_response.content = MagicMock()
    mock_response.content.iter_chunked = lambda _: MockAsyncIterator(chunks)

    # Create a mock for the request coroutine
    request_coro = AsyncMock(return_value=mock_response)
    mock_session.return_value.__aenter__.return_value.request = request_coro

    output_file = tmp_path / "test_output.txt"
    await request.invoke(
        json_data={"test": "data"},
        output_file=str(output_file),
    )

    assert output_file.read_bytes() == b"test data"
