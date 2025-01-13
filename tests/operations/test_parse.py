# # tests/branch_ops/test_parse.py

# from unittest.mock import AsyncMock

# import pytest
# from pydantic import BaseModel

# from lionagi.protocols.generic.event import EventStatus
# from lionagi.service.endpoints.base import APICalling, EndPoint
# from lionagi.service.imodel import iModel
# from lionagi.service.providers.openai_.chat_completions import (
#     CHAT_COMPLETION_CONFIG,
# )
# from lionagi.session.branch import Branch


# class ParseTestModel(BaseModel):
#     field1: str


# def make_mocked_branch_for_parse():
#     """
#     This time we'll attach the mock to parse_model instead of chat_model,
#     depending on how your code retrieves the model in branch.parse(...).
#     """
#     branch = Branch(user="tester_fixture", name="BranchForTests_Parse")

#     async def _fake_invoke(**kwargs):
#         endpoint = EndPoint(config=CHAT_COMPLETION_CONFIG)
#         fake_call = APICalling(
#             payload={},
#             headers={},
#             endpoint=endpoint,
#             is_cached=False,
#             should_invoke_endpoint=False,
#         )
#         fake_call.execution.response = '{"field1":"mocked_response_string"}'
#         fake_call.execution.status = EventStatus.COMPLETED
#         return fake_call

#     mock_invoke = AsyncMock(side_effect=_fake_invoke)
#     mock_parse_model = iModel(
#         "test_mock", model="test_parse_model", api_key="test_key"
#     )
#     mock_parse_model.invoke = mock_invoke

#     # Now set parse_model on the branch:
#     branch.parse_model = mock_parse_model
#     return branch


# @pytest.mark.asyncio
# async def test_parse_basic():
#     """
#     branch.parse(...) => uses parse_model.invoke => "mocked_response_string".
#     Shaped into ParseTestModel(field1='mocked_response_string').
#     """
#     branch = make_mocked_branch_for_parse()

#     res = await branch.parse(
#         text='{"field1":"mocked_response_string"}',
#         request_type=ParseTestModel,
#         max_retries=2,
#         handle_validation="return_value",
#     )
#     assert res.field1 == "mocked_response_string"
#     assert len(branch.messages) == 0
