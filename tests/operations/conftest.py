# tests/branch_ops/conftest.py

from unittest.mock import AsyncMock

import pytest

from lionagi.protocols.generic.event import EventStatus

# Import these so we can construct a real APICalling object:
from lionagi.service.endpoints.base import APICalling
from lionagi.service.imodel import iModel
from lionagi.session.branch import Branch


@pytest.fixture
def branch_with_mock_imodel():
    """
    Provides a Branch with a mock iModel that returns an APICalling
    object with execution.response = {"response": "mocked_response_string"}.
    """
    branch = Branch(user="tester_fixture", name="BranchForTests")

    async def _fake_invoke(**kwargs):
        # Build a real APICalling object so it plays nicely with logging & validation
        fake_call = APICalling(
            payload={},
            headers={},
            endpoint=branch.chat_model.endpoint,  # Some endpoint, real or mock
            is_cached=False,
            should_invoke_endpoint=False,
        )
        # The main thing your code sees is `fake_call.execution.response`
        # which we set to a dict containing "mocked_response_string".
        fake_call.execution.response = "mocked_response_string"
        fake_call.execution.status = EventStatus.COMPLETED
        return fake_call

    async_mock_invoke = AsyncMock(side_effect=_fake_invoke)

    mock_chat_model = iModel(
        provider="test_mock", model="test_chat_model", api_key="test_key"
    )
    mock_chat_model.invoke = async_mock_invoke

    mock_parse_model = iModel(
        provider="test_mock", model="test_parse_model", api_key="test_key"
    )
    mock_parse_model.invoke = async_mock_invoke

    branch.chat_model = mock_chat_model
    branch.parse_model = mock_parse_model
    return branch
