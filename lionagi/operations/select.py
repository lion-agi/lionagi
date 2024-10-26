from __future__ import annotations

import inspect
from collections.abc import Callable
from enum import Enum
from typing import Any

from lion_core.session.branch import Branch
from lion_service import iModel
from lionfuncs import string_similarity
from pydantic import BaseModel, Field

from lionagi.libs.sys_util import SysUtil

from .config import DEFAULT_CHAT_CONFIG

PROMPT = "Please select up to {max_num_selections} items from the following list {choices}. Provide the selection(s) into appropriate field in format required, and no comments from you"


class SelectionModel(BaseModel):
    selected: list[str | Enum] = Field(default_factory=list)


async def select(
    choices: list[str] | type[Enum],
    max_num_selections: int = 1,
    instruction=None,
    guidance=None,
    context=None,
    system=None,
    reason: bool = False,
    actions: bool = False,
    tools: Any = None,
    imodel: iModel = None,
    branch: Branch = None,
    sender=None,
    recipient=None,
    return_enum: bool = False,
    enum_parser: Callable = None,  # parse the model string response to appropriate type
    clear_messages: bool = False,
    system_sender=None,
    system_datetime=None,
    return_branch=False,
    num_parse_retries: int = 3,
    retry_imodel: iModel = None,
    branch_user=None,
    **kwargs,
) -> SelectionModel | tuple[SelectionModel, Branch]:

    if branch and branch.imodel:
        imodel = imodel or branch.imodel
    else:
        imodel = imodel or iModel(**DEFAULT_CHAT_CONFIG)

    selections = []
    if return_enum and not _is_enum(choices):
        raise ValueError("return_enum can only be True if choices is an Enum")

    if _is_enum(choices):
        selections = [selection.value for selection in choices]
    else:
        selections = choices

    prompt = PROMPT.format(
        max_num_selections=max_num_selections, choices=selections
    )

    if instruction:
        prompt = f"{instruction}\n\n{prompt} \n\n "

    branch = branch or Branch(imodel=imodel)
    if branch_user:
        try:
            a = SysUtil.get_id(branch_user)
            branch.user = a
        except:
            branch.user = branch_user
    if system:
        branch.add_message(
            system=system,
            system_datetime=system_datetime,
            system_sender=system_sender,
        )

    kwargs["frozen"] = False
    response_model: SelectionModel = await branch.operate(
        instruction=prompt,
        guidance=guidance,
        context=context,
        sender=sender,
        recipient=recipient,
        reason=reason,
        actions=actions,
        operative_model=SelectionModel,
        clear_messages=clear_messages,
        imodel=imodel,
        num_parse_retries=num_parse_retries,
        retry_imodel=retry_imodel,
        tools=tools,
        **kwargs,
    )

    selected = response_model
    if isinstance(response_model, BaseModel) and hasattr(
        response_model, "selected"
    ):
        selected = response_model.selected
    selected = [selected] if not isinstance(selected, list) else selected
    corrected_selections = [
        string_similarity(
            word=selection,
            correct_words=selections,
            return_most_similar=True,
        )
        for selection in selected
    ]

    if return_enum:
        out = []
        if not enum_parser:
            enum_parser = lambda x: x
        for selection in corrected_selections:
            selection = enum_parser(selection)
            for member in choices.__members__.values():
                if member.value == selection:
                    out.append(member)
        corrected_selections = out

    if isinstance(response_model, BaseModel):
        response_model.selected = corrected_selections

    elif isinstance(response_model, dict):
        response_model["selected"] = corrected_selections

    if return_branch:
        return response_model, branch
    return response_model


def _is_enum(choices):
    return inspect.isclass(choices) and issubclass(choices, Enum)
