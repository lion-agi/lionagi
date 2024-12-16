import json
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest

from lionagi.integrations.openai_.api_endpoints.chat_completions.request.message_models import (
    AssistantMessage,
    SystemMessage,
    UserMessage,
)
from lionagi.integrations.openai_.api_endpoints.chat_completions.request.request_body import (
    OpenAIChatCompletionRequestBody,
)
from lionagi.integrations.openai_.OpenAIModel import OpenAIModel
from lionagi.service.rate_limiter import RateLimitError
from lionagi.service.token_calculator import (
    TiktokenCalculator,
    TokenCalculator,
)

MOCK_PRICE_YAML = """
models:
  gpt-4:
    input_tokens: 0.00003
    output_tokens: 0.00006
    input_tokens_with_batch: 0.000015
    output_tokens_with_batch: 0.00003
"""

MOCK_TOKEN_YAML = """
gpt-4: 8192
gpt-4-0613: 8192
gpt-4-32k: 32768
gpt-4-32k-0613: 32768
gpt-4-turbo-preview: 4096
gpt-4-1106-preview: 4096
gpt-4-0125-preview: 4096
"""


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


class MockTiktokenCalculator(TiktokenCalculator):
    def calculate(self, text: str) -> int:
        if isinstance(text, str):
            return len(text)
        elif isinstance(text, list):
            return sum(len(str(item)) for item in text)
        return 0


@pytest.fixture
def mock_yaml_files():
    # Create a mock that returns different content based on the file path
    def mock_file_content(filename, *args, **kwargs):
        if "price_data.yaml" in str(filename):
            return mock_open(read_data=MOCK_PRICE_YAML).return_value
        elif "max_output_token_data.yaml" in str(filename):
            return mock_open(read_data=MOCK_TOKEN_YAML).return_value
        return mock_open().return_value

    with patch("builtins.open", side_effect=mock_file_content):
        yield


@pytest.fixture
def mock_token_calculator():
    with patch(
        "lionagi.service.token_calculator.TiktokenCalculator",
        MockTiktokenCalculator,
    ):
        yield


@pytest.fixture
def openai_model(mock_yaml_files, mock_token_calculator):
    model = OpenAIModel(
        model="gpt-4",
        api_key="test_key",
        endpoint="chat/completions",
        method="POST",
        content_type="application/json",
        limit_tokens=1000,
        limit_requests=100,
    )
    return model


@pytest.mark.asyncio
async def test_get_input_token_len(openai_model):
    request_body = OpenAIChatCompletionRequestBody(
        model="gpt-4",
        messages=[
            SystemMessage(
                role="system", content="You are a helpful assistant"
            ),
            UserMessage(role="user", content="Hi"),
            AssistantMessage(
                role="assistant", content="Hello! How can I help?"
            ),
            UserMessage(role="user", content="What's the weather?"),
        ],
    )

    token_len = await openai_model.get_input_token_len(request_body)
    assert token_len > 0  # Using mock calculator that returns text length


def test_verify_invoke_viability(openai_model):
    # Test within limits
    assert openai_model.verify_invoke_viability(
        input_tokens_len=10, estimated_output_len=20
    )

    # Test exceeding token limit
    openai_model.rate_limiter.limit_tokens = 25
    openai_model.rate_limiter.remaining_tokens = 25
    assert not openai_model.verify_invoke_viability(
        input_tokens_len=10, estimated_output_len=20
    )

    # Test with no estimated output length
    openai_model.rate_limiter.limit_tokens = 1000
    openai_model.rate_limiter.remaining_tokens = 1000
    assert openai_model.verify_invoke_viability(input_tokens_len=10)


def test_check_limits_info(openai_model):
    headers = {
        "x-ratelimit-limit-requests": "100",
        "x-ratelimit-limit-tokens": "1000",
    }

    # Test updating limits from headers
    openai_model.rate_limiter.limit_requests = None
    openai_model.rate_limiter.limit_tokens = None
    openai_model.check_limits_info(headers)
    assert openai_model.rate_limiter.limit_requests == 100
    assert openai_model.rate_limiter.limit_tokens == 1000

    # Test warning when configured limits exceed headers
    openai_model.rate_limiter.limit_requests = 200
    openai_model.rate_limiter.limit_tokens = 2000
    with pytest.warns(UserWarning):
        openai_model.check_limits_info(headers)


def test_check_remaining_info(openai_model):
    headers = {
        "x-ratelimit-remaining-requests": "95",
        "x-ratelimit-remaining-tokens": "950",
        "Date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
    }

    # Test updating remaining counts
    openai_model.rate_limiter.remaining_requests = 100
    openai_model.rate_limiter.remaining_tokens = 1000
    openai_model.check_remaining_info(headers)
    assert openai_model.rate_limiter.remaining_requests == 95
    assert openai_model.rate_limiter.remaining_tokens == 950
