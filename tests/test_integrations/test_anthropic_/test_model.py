import json
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
from pydantic import ValidationError

from lionagi.integrations.anthropic_.AnthropicModel import AnthropicModel
from lionagi.integrations.anthropic_.api_endpoints.messages.request.message_models import (
    Message,
)
from lionagi.integrations.anthropic_.api_endpoints.messages.request.request_body import (
    AnthropicMessageRequestBody,
)
from lionagi.service.rate_limiter import RateLimitError
from lionagi.service.token_calculator import TiktokenCalculator

MOCK_PRICE_YAML = """
model:
  claude-2:
    input_tokens: 0.00001102
    output_tokens: 0.00003268
  claude-instant-1:
    input_tokens: 0.00000163
    output_tokens: 0.00000551
"""

MOCK_TOKEN_YAML = """
claude-2: 100000
claude-instant-1: 100000
"""


class MockTiktokenCalculator(TiktokenCalculator):
    def calculate(self, text: str) -> int:
        if isinstance(text, str):
            return len(text)
        elif isinstance(text, list):
            return sum(len(str(item)) for item in text)
        return 0


@pytest.fixture
def mock_yaml_files():
    def mock_file_content(filename, *args, **kwargs):
        if "anthropic_price_data.yaml" in str(filename):
            return mock_open(read_data=MOCK_PRICE_YAML).return_value
        elif "anthropic_max_output_token_data.yaml" in str(filename):
            return mock_open(read_data=MOCK_TOKEN_YAML).return_value
        return mock_open().return_value

    with patch("builtins.open", side_effect=mock_file_content):
        yield


@pytest.fixture
def mock_token_calculator():
    with patch(
        "lion.service.token_calculator.TiktokenCalculator",
        MockTiktokenCalculator,
    ):
        yield


@pytest.fixture
def anthropic_model(mock_yaml_files, mock_token_calculator):
    model = AnthropicModel(
        model="claude-2",
        api_key="test_key",
        endpoint="messages",
        method="POST",
        content_type="application/json",
        api_version="2023-06-01",
        limit_tokens=1000,
        limit_requests=100,
    )
    return model


@pytest.mark.asyncio
async def test_get_input_token_len(anthropic_model):
    request_body = AnthropicMessageRequestBody(
        model="claude-2",
        messages=[
            Message(role="user", content="Hi"),
            Message(role="assistant", content="Hello! How can I help?"),
            Message(role="user", content="What's the weather?"),
        ],
        system="You are a helpful assistant",
    )

    token_len = await anthropic_model.get_input_token_len(request_body)
    assert token_len > 0  # Using mock calculator that returns text length

    # Test with mismatched model
    request_body.model = "claude-instant-1"
    with pytest.raises(ValueError, match="Request model does not match"):
        await anthropic_model.get_input_token_len(request_body)


def test_verify_invoke_viability(anthropic_model):
    # Test within limits
    assert anthropic_model.verify_invoke_viability(
        input_tokens_len=10, estimated_output_len=20
    )

    # Test exceeding token limit
    anthropic_model.rate_limiter.limit_tokens = 25
    anthropic_model.rate_limiter.remaining_tokens = 25
    assert not anthropic_model.verify_invoke_viability(
        input_tokens_len=10, estimated_output_len=20
    )

    # Test with no estimated output length
    anthropic_model.rate_limiter.limit_tokens = 1000
    anthropic_model.rate_limiter.remaining_tokens = 1000
    anthropic_model.estimated_output_len = 100  # Set a reasonable default
    assert anthropic_model.verify_invoke_viability(input_tokens_len=10)


def test_estimate_text_price(anthropic_model):
    # Test price estimation
    price = anthropic_model.estimate_text_price(
        input_text="Hello, how are you?",
        estimated_num_of_output_tokens=50,
    )
    assert price > 0

    # Test with no token calculator
    anthropic_model.text_token_calculator = None
    with pytest.raises(ValueError, match="Token calculator not available"):
        anthropic_model.estimate_text_price("test", 10)
