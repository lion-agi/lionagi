# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import AsyncMock, MagicMock

import pytest

from lionagi._errors import TimeoutError
from lionagi.operations.ask.ask import ask
from lionagi.operations.ask.utils import AskAnalysis
from lionagi.protocols.mail.package import PackageCategory
from lionagi.service.imodel import iModel


@pytest.mark.asyncio
async def test_ask_branch_target():
    """Test asking another branch"""
    # Setup mocks
    target_branch = MagicMock()
    target_branch.id = "target_id"
    source_branch = MagicMock()
    source_branch.asend = AsyncMock()
    source_branch.mailbox.await_response = AsyncMock(
        return_value="test response"
    )
    source_branch.operate = AsyncMock(
        return_value=AskAnalysis(response="processed response")
    )

    # Run ask operation
    response = await ask(source_branch, "test query", target_branch)

    # Verify branch communication
    source_branch.asend.assert_called_once()
    call_args = source_branch.asend.call_args[1]
    assert call_args["recipient"] == "target_id"
    assert call_args["category"] == PackageCategory.MESSAGE
    assert isinstance(call_args["request_source"], str)  # ask_id

    # Verify response processing
    assert response == "processed response"


@pytest.mark.asyncio
async def test_ask_model_target():
    """Test asking an iModel directly"""
    # Setup mocks
    model = MagicMock(spec=iModel)
    model.invoke = AsyncMock(return_value="model response")
    branch = MagicMock()
    branch.operate = AsyncMock(
        return_value=AskAnalysis(response="processed response")
    )

    # Run ask operation
    response = await ask(branch, "test query", model)

    # Verify model invocation
    model.invoke.assert_called_once()
    messages = model.invoke.call_args[1]["messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "user"

    # Verify response processing
    assert response == "processed response"


@pytest.mark.asyncio
async def test_ask_external_target():
    """Test asking an external system"""
    # Setup mocks
    branch = MagicMock()
    branch.asend = AsyncMock()
    branch.mailbox.await_response = AsyncMock(return_value="external response")
    branch.operate = AsyncMock(
        return_value=AskAnalysis(response="processed response")
    )

    # Run ask operation
    response = await ask(branch, "test query", "external_system")

    # Verify external communication
    branch.asend.assert_called_once()
    call_args = branch.asend.call_args[1]
    assert call_args["recipient"] == "external_system"
    assert call_args["category"] == PackageCategory.MESSAGE
    assert isinstance(call_args["request_source"], str)  # ask_id

    # Verify response processing
    assert response == "processed response"


@pytest.mark.asyncio
async def test_ask_timeout():
    """Test timeout handling"""
    # Setup mocks
    branch = MagicMock()
    branch.asend = AsyncMock()
    branch.mailbox.await_response = AsyncMock(
        side_effect=TimeoutError("Timeout")
    )

    # Verify timeout handling
    with pytest.raises(TimeoutError):
        await ask(branch, "test query", "target", timeout=1)


def test_ask_analysis_prompt_formatting():
    """Test AskAnalysis prompt formatting"""
    # Test branch target
    branch = MagicMock()
    branch.id = "branch_id"
    prompt = AskAnalysis.format_prompt("test query", branch)
    assert "branch branch_id" in prompt.lower()

    # Test model target
    model = MagicMock(spec=iModel)
    prompt = AskAnalysis.format_prompt("test query", model)
    assert "model" in prompt.lower()

    # Test external target
    prompt = AskAnalysis.format_prompt("test query", "external_system")
    assert "external system" in prompt.lower()
    assert "external_system" in prompt
