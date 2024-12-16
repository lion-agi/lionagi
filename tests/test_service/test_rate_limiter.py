"""Tests for rate_limiter module."""

from datetime import UTC, datetime

import pytest

from lionagi.service.complete_request_info import (
    CompleteRequestInfo,
    CompleteRequestTokenInfo,
)
from lionagi.service.rate_limiter import RateLimiter, RateLimitError


def test_rate_limiter_initialization():
    """Test RateLimiter initialization with different parameters."""
    limiter = RateLimiter(limit_tokens=1000, limit_requests=10)
    assert limiter.limit_tokens == 1000
    assert limiter.limit_requests == 10
    assert limiter.remaining_tokens is None
    assert limiter.remaining_requests is None
    assert limiter.last_check_timestamp is None
    assert len(limiter.unreleased_requests) == 0


def test_append_complete_request_token_info():
    """Test appending token request info."""
    limiter = RateLimiter(limit_tokens=1000, limit_requests=10)
    timestamp = datetime.now(UTC).timestamp()
    info = CompleteRequestTokenInfo(timestamp=timestamp, token_usage=100)

    limiter.append_complete_request_token_info(info)
    assert limiter.remaining_tokens == 900
    assert limiter.remaining_requests == 9
    assert len(limiter.unreleased_requests) == 1


def test_append_complete_request_info():
    """Test appending request info without tokens."""
    limiter = RateLimiter(limit_tokens=1000, limit_requests=10)
    timestamp = datetime.now(UTC).timestamp()
    info = CompleteRequestInfo(timestamp=timestamp)

    limiter.append_complete_request_token_info(info)
    assert (
        limiter.remaining_tokens is None
    )  # Should not change without token info
    assert limiter.remaining_requests == 9
    assert len(limiter.unreleased_requests) == 1


def test_no_limits():
    """Test behavior when no limits are set."""
    limiter = RateLimiter()
    timestamp = datetime.now(UTC).timestamp()
    info = CompleteRequestTokenInfo(timestamp=timestamp, token_usage=100)

    limiter.append_complete_request_token_info(info)
    assert limiter.remaining_tokens is None
    assert limiter.remaining_requests is None
    assert len(limiter.unreleased_requests) == 0


def test_release_tokens():
    """Test token release after time window."""
    limiter = RateLimiter(limit_tokens=1000, limit_requests=10)
    old_timestamp = datetime.now(UTC).timestamp() - 61  # 61 seconds ago
    recent_timestamp = datetime.now(UTC).timestamp()

    # Add old request
    old_info = CompleteRequestTokenInfo(
        timestamp=old_timestamp, token_usage=100
    )
    limiter.append_complete_request_token_info(old_info)

    # Add recent request
    recent_info = CompleteRequestTokenInfo(
        timestamp=recent_timestamp, token_usage=100
    )
    limiter.append_complete_request_token_info(recent_info)

    initial_tokens = limiter.remaining_tokens
    initial_requests = limiter.remaining_requests

    limiter.release_tokens()

    # Old request should be released, recent one should remain
    assert limiter.remaining_tokens == initial_tokens + 100
    assert limiter.remaining_requests == initial_requests + 1
    assert len(limiter.unreleased_requests) == 1


def test_check_availability():
    """Test availability checking."""
    limiter = RateLimiter(limit_tokens=1000, limit_requests=10)
    limiter.remaining_tokens = 500
    limiter.remaining_requests = 5

    # Test within limits
    assert limiter.check_availability(
        request_token_len=200, estimated_output_len=200
    )

    # Test exceeding token limit
    assert not limiter.check_availability(
        request_token_len=300, estimated_output_len=300
    )

    # Test exceeding request limit
    limiter.remaining_requests = 0
    assert not limiter.check_availability(
        request_token_len=100, estimated_output_len=100
    )


def test_rate_limit_error():
    """Test RateLimitError."""
    input_tokens = 100
    output_tokens = 200
    error = RateLimitError("Rate limit exceeded", input_tokens, output_tokens)
    assert error.requested_tokens == 300
    assert str(error) == "Rate limit exceeded"


def test_update_rate_limit():
    """Test updating rate limit from HTTP response."""
    limiter = RateLimiter(limit_tokens=1000, limit_requests=10)
    date_str = "Wed, 21 Oct 2023 07:28:00 GMT"

    # Test with token usage
    limiter.update_rate_limit(date_str, total_token_usage=100)
    assert len(limiter.unreleased_requests) == 1
    assert limiter.remaining_tokens == 900
    assert limiter.remaining_requests == 9

    # Test without token usage
    limiter.update_rate_limit(date_str)
    assert len(limiter.unreleased_requests) == 2
    assert (
        limiter.remaining_tokens == 900
    )  # Should not change without token usage
    assert limiter.remaining_requests == 8


def test_model_fields():
    """Test that model fields are properly defined."""
    limiter = RateLimiter(limit_tokens=1000, limit_requests=10)
    assert "limit_tokens" in limiter.model_fields
    assert "limit_requests" in limiter.model_fields
    assert "remaining_tokens" in limiter.model_fields
    assert "remaining_requests" in limiter.model_fields
    assert "last_check_timestamp" in limiter.model_fields
    assert "unreleased_requests" in limiter.model_fields

    # Check field descriptions
    assert (
        limiter.model_fields["last_check_timestamp"].description
        == "Last time to check tokens and requests."
    )
    assert (
        limiter.model_fields["unreleased_requests"].description
        == "completed request info for replenish"
    )
