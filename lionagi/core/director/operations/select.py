from __future__ import annotations

from collections.abc import Callable
from enum import Enum

from lionfuncs import choose_most_similar
from pydantic import BaseModel

from lionagi.core.director.models import ReasonModel
from lionagi.core.session.branch import Branch

from .utils import is_enum

PROMPT = "Please select up to {max_num_selections} items from the following list {choices}. Provide the selection(s), and no comments from you"


class SelectionModel(BaseModel):
    selected: list[str | Enum]


class ReasonSelectionModel(BaseModel):
    selected: list[str | Enum]
    reason: ReasonModel


async def select(
    choices: list[str] | type[Enum],
    max_num_selections: int = 1,
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    reason: bool = False,
    return_enum: bool = False,
    enum_parser: Callable = None,  # parse the model string response to appropriate type
    branch: Branch = None,
    return_pydantic_model=False,
    **kwargs,  # additional chat arguments
):
    selections = []
    if return_enum and not is_enum(choices):
        raise ValueError("return_enum can only be True if choices is an Enum")

    if is_enum(choices):
        selections = [selection.value for selection in choices]
    else:
        selections = choices

    prompt = PROMPT.format(
        max_num_selections=max_num_selections, choices=selections
    )

    if instruction:
        prompt = f"{instruction}\n\n{prompt} \n\n "

    branch = branch or Branch()
    response: SelectionModel | ReasonSelectionModel | str = await branch.chat(
        instruction=prompt,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        pydantic_model=SelectionModel if not reason else ReasonSelectionModel,
        return_pydantic_model=True,
        **kwargs,
    )

    selected = response
    if isinstance(response, SelectionModel | ReasonSelectionModel):
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

    if return_pydantic_model:
        if not isinstance(response, SelectionModel | ReasonSelectionModel):
            return SelectionModel(selected=corrected_selections)
        response.selected = corrected_selections
        return response
    return corrected_selections
