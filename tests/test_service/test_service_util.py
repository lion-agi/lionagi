"""Tests for service_util module."""

import asyncio
from unittest.mock import Mock, patch

import pytest

from lionagi.service.rate_limiter import RateLimitError
from lionagi.service.service_util import invoke_retry


class MockRequestModel:
    def __init__(self):
        self.rate_limiter = Mock()
        self.rate_limiter.limit_tokens = 1000
        self.rate_limiter.check_availability = Mock(return_value=True)


@pytest.mark.asyncio
async def test_invoke_retry_success():
    """Test successful invocation without retries."""

    async def mock_func(model):
        return "success"

    decorated = invoke_retry()(mock_func)
    result = await decorated(MockRequestModel())

    assert result == "success"


@pytest.mark.asyncio
async def test_invoke_retry_with_rate_limit_error():
    """Test retry behavior with RateLimitError."""
    request_model = MockRequestModel()

    # Mock function that fails with RateLimitError first, then succeeds
    call_count = 0

    async def test_func(model):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RateLimitError("Rate limit exceeded", 100, 100)
        return "success"

    decorated = invoke_retry(max_retries=3, base_delay=1)(test_func)
    result = await decorated(request_model)

    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_invoke_retry_with_http_429():
    """Test retry behavior with HTTP 429 error."""

    class HTTPError(Exception):
        def __init__(self, status):
            self.status = status
            self.headers = {}

    # Mock function that fails with 429 first, then succeeds
    call_count = 0

    async def test_func(model):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise HTTPError(429)
        return "success"

    decorated = invoke_retry(max_retries=3, base_delay=1)(test_func)
    result = await decorated(MockRequestModel())

    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_invoke_retry_with_retry_after_header():
    """Test retry behavior with Retry-After header."""

    class HTTPError(Exception):
        def __init__(self, status, headers):
            self.status = status
            self.headers = headers

    # Mock function that fails with 429 and Retry-After header, then succeeds
    call_count = 0

    async def test_func(model):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise HTTPError(429, {"Retry-After": "1"})
        return "success"

    decorated = invoke_retry(max_retries=3, base_delay=1)(test_func)
    result = await decorated(MockRequestModel())

    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_invoke_retry_max_retries_exceeded():
    """Test behavior when max retries is exceeded."""

    async def test_func(model):
        raise Exception("Persistent error")

    decorated = invoke_retry(max_retries=2, base_delay=1)(test_func)

    with pytest.raises(Exception, match="Persistent error"):
        await decorated(MockRequestModel())


@pytest.mark.asyncio
async def test_invoke_retry_invalid_max_retries():
    """Test validation of max_retries parameter."""

    async def test_func(model):
        return "success"

    decorated = invoke_retry(max_retries=0)(test_func)

    with pytest.raises(ValueError, match="Invalid max number of retries"):
        await decorated(MockRequestModel())


@pytest.mark.asyncio
async def test_invoke_retry_quota_exceeded():
    """Test behavior when account quota is exceeded."""

    class QuotaError(Exception):
        def __init__(self):
            self.status = 429
            self.message = "exceeded your current quota"

    async def test_func(model):
        raise QuotaError()

    decorated = invoke_retry(max_retries=2, base_delay=1)(test_func)

    with pytest.raises(QuotaError):
        await decorated(MockRequestModel())


@pytest.mark.asyncio
async def test_invoke_retry_token_limit_exceeded():
    """Test behavior when token limit is exceeded."""
    request_model = MockRequestModel()
    request_model.rate_limiter.limit_tokens = 500

    async def test_func(model):
        raise RateLimitError(
            "Rate limit exceeded", 300, 300
        )  # Total 600 tokens

    decorated = invoke_retry(max_retries=2, base_delay=1)(test_func)

    with pytest.raises(
        ValueError, match="Requested tokens exceed the model's token limit"
    ):
        await decorated(request_model)


@pytest.mark.asyncio
async def test_invoke_retry_server_error():
    """Test retry behavior with server errors (5xx)."""
    call_count = 0

    async def test_func(model):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            error = Exception()
            error.status = 500
            error.headers = {}
            raise error
        return "success"

    decorated = invoke_retry(max_retries=2, base_delay=1)(test_func)
    result = await decorated(MockRequestModel())

    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_invoke_retry_exponential_backoff():
    """Test exponential backoff behavior."""
    sleep_times = []

    async def mock_sleep(seconds):
        sleep_times.append(seconds)

    call_count = 0

    async def test_func(model):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            error = Exception()
            error.status = 429
            error.headers = {}
            raise error
        return "success"

    decorated = invoke_retry(max_retries=3, base_delay=1)(test_func)

    with patch("asyncio.sleep", mock_sleep):
        result = await decorated(MockRequestModel())

    assert result == "success"
    assert len(sleep_times) == 2
    assert sleep_times[1] > sleep_times[0]  # Second delay should be longer


@pytest.mark.asyncio
async def test_invoke_retry_max_delay():
    """Test that delay doesn't exceed max_delay."""
    sleep_times = []

    async def mock_sleep(seconds):
        sleep_times.append(seconds)

    call_count = 0

    async def test_func(model):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            error = Exception()
            error.status = 429
            error.headers = {}
            raise error
        return "success"

    max_delay = 5
    decorated = invoke_retry(max_retries=3, base_delay=2, max_delay=max_delay)(
        test_func
    )

    with patch("asyncio.sleep", mock_sleep):
        result = await decorated(MockRequestModel())

    assert result == "success"
    assert all(delay <= max_delay for delay in sleep_times)
