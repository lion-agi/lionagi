# tests/branch_ops/test_interpret.py

from unittest.mock import AsyncMock

import pytest

from lionagi.protocols.generic.event import EventStatus
from lionagi.service.endpoints.base import APICalling, EndPoint
from lionagi.service.imodel import iModel
from lionagi.service.providers.openai_.chat_completions import (
    CHAT_COMPLETION_CONFIG,
)
from lionagi.session.branch import Branch


def make_mocked_branch_for_interpret():
    branch = Branch(user="tester_fixture", name="BranchForTests_Interpret")

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

    mock_invoke = AsyncMock(side_effect=_fake_invoke)
    mock_chat_model = iModel(
        "test_mock", model="test_chat_model", api_key="test_key"
    )
    mock_chat_model.invoke = mock_invoke

    branch.chat_model = mock_chat_model
    return branch


@pytest.mark.asyncio
async def test_interpret_basic():
    """
    branch.interpret(...) => calls branch.communicate(...) with skip_validation,
    returning 'mocked_response_string'.
    """
    branch = make_mocked_branch_for_interpret()

    refined_prompt = await branch.interpret(
        text="User's raw input", domain="some_domain", style="concise"
    )
    assert refined_prompt == "mocked_response_string"
    assert len(branch.messages) == 0
