from collections.abc import Callable
from enum import Enum
from typing import Any, Literal

from lionfuncs import choose_most_similar
from pydantic import field_validator

from lionagi.core.operative.operative import Operative
from lionagi.core.session.branch import Branch

from .prompt import PROMPT
from .utils import is_enum


class SelectModel(Operative):
    selected: list = []

    @field_validator("selected", mode="before")
    def validate_selected(cls, value) -> list:
        return [value] if not isinstance(value, list) else value


async def select(
    choices: list[Any] | type[Enum],
    max_num_selections: int = 1,
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    tools=None,
    reason: bool = False,
    actions: bool = False,
    invoke_action: bool = True,
    max_num_actions: int | Literal["auto"] = "auto",
    return_enum: bool = False,
    enum_parser: Callable = None,  # parse the model string response to appropriate type
    branch=None,
    return_branch=False,
    **kwargs,
):
    if return_enum and not is_enum(choices):
        raise ValueError("return_enum can only be True if choices is an Enum")

    selections = (
        [selection.value for selection in choices]
        if is_enum(choices)
        else choices
    )
    prompt = PROMPT.format(
        max_num_selections=max_num_selections, choices=selections
    )

    if instruction:
        prompt = f"{instruction}\n{prompt}\n"

    branch = branch or Branch()

    response = await branch.operate(
        operative=SelectModel,
        intruction=prompt,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        tools=tools,
        reason=reason,
        actions=actions,
        invoke_action=invoke_action,
        max_num_actions=max_num_actions,
        **kwargs,
    )

    selected = response
    if hasattr(response, "selected"):
        selected = response.selected

    selected = [selected] if not isinstance(selected, list) else selected
    corrected_selections = [
        choose_most_similar(selection, selections) for selection in selected
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

    response.selected = corrected_selections
    if return_branch:
        return response, branch
    return response
