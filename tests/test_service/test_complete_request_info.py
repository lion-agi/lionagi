"""Tests for complete_request_info module."""

import pytest

from lionagi.service.complete_request_info import (
    CompleteRequestInfo,
    CompleteRequestTokenInfo,
)


def test_complete_request_info():
    """Test CompleteRequestInfo model."""
    timestamp = 1234567890.123
    info = CompleteRequestInfo(timestamp=timestamp)
    assert info.timestamp == timestamp


def test_complete_request_token_info():
    """Test CompleteRequestTokenInfo model."""
    timestamp = 1234567890.123
    token_usage = 100
    info = CompleteRequestTokenInfo(
        timestamp=timestamp, token_usage=token_usage
    )
    assert info.timestamp == timestamp
    assert info.token_usage == token_usage


def test_complete_request_token_info_inheritance():
    """Test that CompleteRequestTokenInfo inherits from CompleteRequestInfo."""
    info = CompleteRequestTokenInfo(timestamp=1234567890.123, token_usage=100)
    assert isinstance(info, CompleteRequestInfo)


def test_complete_request_info_validation():
    """Test validation of CompleteRequestInfo."""
    with pytest.raises(ValueError):
        CompleteRequestInfo(timestamp="not a float")


def test_complete_request_token_info_validation():
    """Test validation of CompleteRequestTokenInfo."""
    with pytest.raises(ValueError):
        CompleteRequestTokenInfo(
            timestamp=1234567890.123, token_usage="not an int"
        )

    with pytest.raises(ValueError):
        CompleteRequestTokenInfo(timestamp="not a float", token_usage=100)


def test_complete_request_info_model_fields():
    """Test model fields are properly defined."""
    info = CompleteRequestInfo(timestamp=1234567890.123)
    assert "timestamp" in info.model_fields
    assert (
        info.model_fields["timestamp"].description
        == "HTTP response generated time"
    )


def test_complete_request_token_info_model_fields():
    """Test model fields are properly defined."""
    info = CompleteRequestTokenInfo(timestamp=1234567890.123, token_usage=100)
    assert "timestamp" in info.model_fields
    assert "token_usage" in info.model_fields
    assert (
        info.model_fields["token_usage"].description
        == "Number of tokens used in the request"
    )
