# # tests/branch_ops/test_chat.py

# from unittest.mock import AsyncMock

# import pytest

# from lionagi.protocols.generic.event import EventStatus
# from lionagi.service.endpoints.base import APICalling, EndPoint
# from lionagi.service.imodel import iModel
# from lionagi.session.branch import Branch


# def make_mocked_branch_for_chat():
#     """
#     Build a Branch instance with a custom iModel mock that returns 'mocked_response_string'
#     for test_chat use.
#     """
#     branch = Branch(user="tester_fixture", name="BranchForTests_Chat")

#     async def _fake_invoke(**kwargs):
#         # Make a real APICalling so that logging/validation doesn't break
#         from lionagi.service.providers.openai_.chat_completions import (
#             CHAT_COMPLETION_CONFIG,
#         )

#         endpoint = EndPoint(config=CHAT_COMPLETION_CONFIG)
#         fake_call = APICalling(
#             payload={},
#             headers={},
#             endpoint=endpoint,  # or a real/mocked endpoint
#             is_cached=False,
#             should_invoke_endpoint=False,
#         )
#         # The key part: let .execution.response be a dict with 'response': 'mocked_response_string'
#         fake_call.execution.response = "mocked_response_string"
#         fake_call.execution.status = EventStatus.COMPLETED
#         return fake_call

#     async_mock_invoke = AsyncMock(side_effect=_fake_invoke)

#     mock_chat_model = iModel(
#         provider="test_mock",
#         model="test_chat_model",
#         api_key="test_key",
#         invoke_with_endpoint=False,
#     )
#     mock_chat_model.invoke = async_mock_invoke

#     branch.chat_model = mock_chat_model
#     return branch


# @pytest.mark.asyncio
# async def test_chat_basic():
#     """
#     Test that branch.chat(...) uses the mocked iModel and returns 'mocked_response_string'.
#     """
#     branch = make_mocked_branch_for_chat()
#     ins, assistant_res = await branch.chat(
#         instruction="Hello from user!", return_ins_res_message=True
#     )

#     # The mock iModel yields "mocked_response_string"
#     assert assistant_res.response == "mocked_response_string"

#     # Check messages got stored (assuming your code does that)
#     assert len(branch.messages) == 0
#     assert ins.instruction == "Hello from user!"
#     assert assistant_res.response == "mocked_response_string"
