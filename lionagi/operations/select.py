from collections.abc import Callable
from enum import Enum
from inspect import isclass
from typing import Any

from lionfuncs import choose_most_similar
from pydantic import field_validator

from lionagi.core.operative.operative import Operative
from lionagi.core.session.branch import Branch


def is_enum(choices):
    return isclass(choices) and issubclass(choices, Enum)


PROMPT = "Please select up to {max_num_selections} items from the following list {choices}. Provide the selection(s), and no comments from you"


class SelectModel(Operative):

    selected: list = []

    @field_validator("selected", mode="before")
    def validate_selected(cls, value) -> list:
        return [value] if not isinstance(value, list) else value


async def select(
    choices: list[Any] | type[Enum],
    max_num_selections: int = 1,
    instruction=None,
    guidance=None,
    context=None,
    system=None,
    reason: bool = False,
    actions: bool = False,
    tools: Any = None,
    branch: Branch = None,
    sender=None,
    recipient=None,
    progress=None,
    clear_messages: bool = False,
    system_sender=None,
    system_datetime=None,
    return_branch=False,
    invoke_action: bool = True,
    return_enum: bool = False,
    enum_parser: Callable = None,  # parse the model string response to appropriate type
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

    if system:
        branch.add_message(
            system=system,
            system_datetime=system_datetime,
            sender=system_sender,
        )

    response = await branch.operate(
        instruction=instruction,
        guidance=guidance,
        context=(
            [{"operation": prompt}, context]
            if context
            else {"operation": prompt}
        ),
        sender=sender,
        recipient=recipient,
        reason=reason,
        actions=actions,
        tools=tools,
        progress=progress,
        clear_messages=clear_messages,
        operative_model=SelectModel,
        invoke_action=invoke_action,
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
