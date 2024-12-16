from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from lionagi.integrations.perplexity_.api_endpoints.chat_completions.request.request_body import (
    Message,
    PerplexityChatCompletionRequestBody,
)
from lionagi.integrations.perplexity_.PerplexityModel import PerplexityModel
from lionagi.service.rate_limiter import RateLimitError


@pytest.fixture
def perplexity_model():
    return PerplexityModel(
        model="llama-3.1-sonar-small-128k-online",
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
        limit_tokens=1000,
        limit_requests=100,
    )


@pytest.mark.asyncio
async def test_get_input_token_len(perplexity_model):
    request_body = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[Message(role="user", content="Hi")],
    )

    token_len = await perplexity_model.get_input_token_len(request_body)
    assert token_len > 0

    # Test model mismatch
    request_body.model = "different-model"
    with pytest.raises(ValueError, match="Request model does not match"):
        await perplexity_model.get_input_token_len(request_body)


def test_verify_invoke_viability(perplexity_model):
    # Test with no tokens used
    assert perplexity_model.verify_invoke_viability(
        input_tokens_len=10, estimated_output_len=10
    )

    # Test with tokens exceeding limit
    perplexity_model.rate_limiter.limit_tokens = 10
    perplexity_model.rate_limiter.remaining_tokens = 5
    assert not perplexity_model.verify_invoke_viability(
        input_tokens_len=10, estimated_output_len=10
    )


def test_estimate_text_price(perplexity_model):
    price = perplexity_model.estimate_text_price(
        "Hello", estimated_num_of_output_tokens=10
    )
    assert price > 0

    # Test with no token calculator
    perplexity_model.text_token_calculator = None
    with pytest.raises(ValueError, match="Token calculator not available"):
        perplexity_model.estimate_text_price("Hello")


@pytest.mark.asyncio
async def test_invoke_with_rate_limit_error(perplexity_model):
    request_body = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[Message(role="user", content="Hi" * 1000)],  # Large input
    )

    perplexity_model.rate_limiter.limit_tokens = 100
    perplexity_model.rate_limiter.remaining_tokens = 100

    with pytest.raises(
        ValueError, match="Requested tokens exceed the model's token limit"
    ):
        await perplexity_model.invoke(request_body)


@pytest.mark.asyncio
async def test_stream_functionality(perplexity_model):
    request_body = PerplexityChatCompletionRequestBody(
        model="llama-3.1-sonar-small-128k-online",
        messages=[Message(role="user", content="Hi")],
        stream=True,
    )

    mock_chunks = [
        {"id": "1", "choices": [{"message": {"content": "Hello"}}]},
        {"id": "2", "choices": [{"message": {"content": "!"}}]},
        {"usage": {"total_tokens": 10}},
    ]

    class MockAsyncIterator:
        def __init__(self, chunks):
            # Format date in the expected format: Thu, 01 Jan 1970 00:00:00 GMT
            date_str = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            self.chunks = [{"headers": {"date": date_str}}] + chunks
            self.index = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.index >= len(self.chunks):
                raise StopAsyncIteration
            chunk = self.chunks[self.index]
            self.index += 1
            return chunk

    with patch.object(
        perplexity_model.request_model,
        "stream",
        return_value=MockAsyncIterator(mock_chunks),
    ):
        response = await perplexity_model.stream(request_body)
        assert len(response) == len(mock_chunks)
        assert response[0]["id"] == "1"
        assert response[1]["id"] == "2"
        assert response[2]["usage"]["total_tokens"] == 10
