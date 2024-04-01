from typing import Callable
from ..tool import func_to_tool, Tool

import contextlib
from lionagi.libs import ParseUtil, StringMatch, convert, func_call


def _parse_out(out_):
    if isinstance(out_, str):
        try:
            out_ = ParseUtil.md_to_json(out_)
        except Exception:
            with contextlib.suppress(Exception):
                out_ = ParseUtil.fuzzy_parse_json(out_.strip("```json").strip("```"))
    return out_


def _process_tools(tool_obj, branch):
    if isinstance(tool_obj, Callable):
        _process_tool(tool_obj, branch)
    else:
        for i in tool_obj:
            _process_tool(i, branch)


def _process_tool(tool_obj, branch):
    if (
        isinstance(tool_obj, Tool)
        and tool_obj.schema_["function"]["name"] not in branch.tool_manager.registry
    ):
        branch.register_tools(tool_obj)
    if isinstance(tool_obj, Callable):
        tool = func_to_tool(tool_obj)[0]
        if tool.schema_["function"]["name"] not in branch.tool_manager.registry:
            branch.register_tools(tool)


# def _handle_single_out(
#     dict_,
#     default_key="answer",
#     choices=None,
#     to_type="dict",
#     to_type_kwargs=None,
#     to_default=True,
# ):

#     if to_type_kwargs is None:
#         to_type_kwargs = {}
#     dict_ = _parse_out(dict_)

#     if default_key not in dict_:
#         raise ValueError(f"Key {default_key} not found in output")

#     answer = dict_[default_key]

#     if (
#         choices is not None
#         and answer not in choices
#         and convert.strip_lower(dict_) in ["", "none", "null", "na", "n/a"]
#     ):
#         raise ValueError(f"Answer {answer} not in choices {choices}")

#     if to_type == "str":
#         answer = convert.to_str(answer, **to_type_kwargs)

#     elif to_type == "num":
#         answer = convert.to_num(answer, **to_type_kwargs)

#     dict_[default_key] = answer

#     return answer if to_default else dict_


# def _handle_multi_out(
#     dict_,
#     default_key="answer",
#     choices=None,
#     to_type="dict",
#     to_type_kwargs=None,
#     to_default=True,
#     include_mapping=False,
# ):
#     if to_type_kwargs is None:
#         to_type_kwargs = {}

#     if include_mapping:
#         for i in dict_:
#             i[default_key] = _handle_single_out(
#                 i[default_key],
#                 choices=choices,
#                 default_key=default_key,
#                 to_type=to_type,
#                 to_type_kwargs=to_type_kwargs,
#                 to_default=to_default,
#             )
#     else:
#         _out = []
#         for i in dict_:
#             i = _handle_single_out(
#                 i,
#                 choices=choices,
#                 default_key=default_key,
#                 to_type=to_type,
#                 to_type_kwargs=to_type_kwargs,
#                 to_default=to_default,
#             )
#             _out.append(i)
#         return _out

#     return dict_ if len(dict_) > 1 else dict_[0]
