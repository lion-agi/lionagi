import os
from unittest.mock import AsyncMock, patch

import pytest

from lionagi.integrations.litellm_.imodel import RESERVED_PARAMS, LiteiModel


@pytest.fixture
def model_kwargs():
    return {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Hello"}],
        "api_key": "OPENAI_API_KEY",  # This is the env var name
    }


@pytest.fixture
def model_instance(model_kwargs):
    return LiteiModel(**model_kwargs)


def test_init_with_env_api_key(monkeypatch):
    # Setup
    monkeypatch.setenv("TEST_API_KEY", "test-key-123")
    model = LiteiModel(api_key="TEST_API_KEY")

    # Verify the api_key_schema stores the env var name
    assert model.api_key_schema == "TEST_API_KEY"
    # Verify the actual api_key in kwargs is the resolved value
    assert model.kwargs["api_key"] == "test-key-123"


def test_init_with_direct_api_key():
    # Setup
    direct_key = "direct-key-123"
    model = LiteiModel(api_key=direct_key)

    # Verify
    assert model.kwargs["api_key"] == direct_key
    assert not hasattr(model, "api_key_schema")


def test_to_dict(model_instance, model_kwargs):
    # Execute
    result = model_instance.to_dict()

    # Verify - should include model, messages, and original api_key schema
    expected = {
        "model": model_kwargs["model"],
        "messages": model_kwargs["messages"],
        "api_key": model_kwargs[
            "api_key"
        ],  # Should be the original env var name
    }
    assert result == expected


def test_from_dict(model_kwargs, monkeypatch):
    # Setup env var
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-456")

    # Execute
    model = LiteiModel.from_dict(model_kwargs)

    # Verify
    assert isinstance(model, LiteiModel)
    assert model.api_key_schema == model_kwargs["api_key"]
    assert model.kwargs["api_key"] == "test-key-456"  # Resolved value
    assert model.kwargs["model"] == model_kwargs["model"]
    assert model.kwargs["messages"] == model_kwargs["messages"]


@pytest.mark.asyncio
async def test_invoke():
    # Setup
    model = LiteiModel(model="gpt-4")
    mock_response = {"choices": [{"message": {"content": "Hello!"}}]}

    # Mock the acompletion method
    with patch.object(
        model, "acompletion", new_callable=AsyncMock
    ) as mock_acompletion:
        mock_acompletion.return_value = mock_response

        # Execute
        result = await model.invoke(
            messages=[{"role": "user", "content": "Hi"}]
        )

        # Verify
        assert result == mock_response
        mock_acompletion.assert_called_once_with(
            model="gpt-4", messages=[{"role": "user", "content": "Hi"}]
        )


@pytest.mark.asyncio
async def test_invoke_removes_reserved_params():
    # Setup
    model = LiteiModel(
        model="gpt-4",
        invoke_action="test",
        instruction="test",
        clear_messages=True,
    )
    mock_response = {"choices": [{"message": {"content": "Hello!"}}]}

    # Mock the acompletion method
    with patch.object(
        model, "acompletion", new_callable=AsyncMock
    ) as mock_acompletion:
        mock_acompletion.return_value = mock_response

        # Execute
        result = await model.invoke()

        # Verify
        assert result == mock_response
        called_kwargs = mock_acompletion.call_args[1]
        for param in RESERVED_PARAMS:
            assert param not in called_kwargs


def test_hash(model_instance):
    # Execute
    hash_value = hash(model_instance)

    # Verify it's an integer (hash value)
    assert isinstance(hash_value, int)

    # Create a new instance with same params
    model2 = LiteiModel(**model_instance.kwargs)
    assert hash(model_instance) == hash(model2)


def test_hash_equality():
    # Setup - use only hashable types for testing
    model1 = LiteiModel(model="gpt-4", temperature=0.7)
    model2 = LiteiModel(model="gpt-4", temperature=0.7)
    model3 = LiteiModel(model="gpt-4", temperature=0.8)

    # Verify
    assert hash(model1) == hash(model2)
    assert hash(model1) != hash(model3)
