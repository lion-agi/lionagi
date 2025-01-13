# tests/branch_ops/test_instruct.py

from unittest.mock import AsyncMock

import pytest

from lionagi.operatives.types import Instruct
from lionagi.protocols.generic.event import EventStatus
from lionagi.service.endpoints.base import APICalling, EndPoint
from lionagi.service.imodel import iModel
from lionagi.service.providers.openai_.chat_completions import (
    CHAT_COMPLETION_CONFIG,
)
from lionagi.session.branch import Branch


def make_mocked_branch_for_instruct():
    branch = Branch(user="tester_fixture", name="BranchForTests_Instruct")

    async def _fake_invoke(**kwargs):
        endpoint = EndPoint(config=CHAT_COMPLETION_CONFIG)
        fake_call = APICalling(
            payload={},
            headers={},
            endpoint=endpoint,
            is_cached=False,
            should_invoke_endpoint=False,
        )
        fake_call.execution.response = "mocked_response_string"
        fake_call.execution.status = EventStatus.COMPLETED
        return fake_call

    async_mock_invoke = AsyncMock(side_effect=_fake_invoke)

    mock_chat_model = iModel(
        "test_mock", model="test_chat_model", api_key="test_key"
    )
    mock_chat_model.invoke = async_mock_invoke

    branch.chat_model = mock_chat_model
    return branch


@pytest.mark.asyncio
async def test_instruct_no_actions():
    """
    If Instruct(actions=False), we expect branch.instruct() to call communicate or similar.
    """
    branch = make_mocked_branch_for_instruct()
    instruct_obj = Instruct(instruction="No actions needed")

    result = await branch.instruct(instruct_obj)
    assert result == "mocked_response_string"

    assert len(branch.messages) == 2


@pytest.mark.asyncio
async def test_instruct_with_actions():
    """
    If instruct.actions=True => uses branch.operate(...).
    """
    branch = make_mocked_branch_for_instruct()
    instruct_obj = Instruct(instruction="Need a tool call", actions=True)

    result = await branch.instruct(instruct_obj, skip_validation=True)
    assert result == "mocked_response_string"
    assert len(branch.messages) == 2
