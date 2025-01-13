# # tests/branch_ops/test_select.py

# from unittest.mock import AsyncMock

# import pytest

# from lionagi.protocols.generic.event import EventStatus
# from lionagi.service.endpoints.base import APICalling, EndPoint
# from lionagi.service.imodel import iModel
# from lionagi.service.providers.openai_.chat_completions import (
#     CHAT_COMPLETION_CONFIG,
# )
# from lionagi.session.branch import Branch


# def make_mocked_branch_for_select():
#     branch = Branch(user="tester_fixture", name="BranchForTests_Select")

#     async def _fake_invoke(**kwargs):
#         endpoint = EndPoint(config=CHAT_COMPLETION_CONFIG)
#         fake_call = APICalling(
#             payload={},
#             headers={},
#             endpoint=endpoint,
#             is_cached=False,
#             should_invoke_endpoint=False,
#         )
#         fake_call.execution.response = '{"selected": ["Option2"]}'
#         fake_call.execution.status = EventStatus.COMPLETED
#         return fake_call

#     mock_invoke = AsyncMock(side_effect=_fake_invoke)
#     mock_chat_model = iModel(
#         "test_mock", model="test_chat_model", api_key="test_key"
#     )
#     mock_chat_model.invoke = mock_invoke

#     branch.chat_model = mock_chat_model
#     return branch


# @pytest.mark.asyncio
# async def test_select_basic():
#     """
#     branch.select(...) => uses the LLM to pick from a list of choices.
#     The final parse is "mocked_response_string", presumably mapped to a 'selected' field.
#     """
#     branch = make_mocked_branch_for_select()

#     choices = ["Option1", "Option2", "Option3"]
#     result = await branch.select(
#         instruct={"instruction": "Pick the best option."},
#         choices=choices,
#         max_num_selections=1,
#     )
#     # For demonstration, let's just check it's not empty:
#     assert result.selected
#     assert len(branch.messages) == 2
