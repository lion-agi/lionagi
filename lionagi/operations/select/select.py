# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from lionagi.operatives.types import Instruct
from lionagi.session.branch import Branch

from .prompt import PROMPT
from .utils import parse_selection, parse_to_representation


class SelectionModel(BaseModel):
    """Model representing the selection output."""

    selected: list[Any] = Field(default_factory=list)


async def select(
    instruct: Instruct | dict[str, Any],
    choices: list[str] | type[Enum] | dict[str, Any],
    max_num_selections: int = 1,
    branch: Branch | None = None,
    branch_kwargs: dict[str, Any] | None = None,
    return_branch: bool = False,
    verbose: bool = False,
    **kwargs: Any,
) -> SelectionModel | tuple[SelectionModel, Branch]:
    """Perform a selection operation from given choices.

    Args:
        instruct: Instruction model or dictionary.
        choices: Options to select from.
        max_num_selections: Maximum selections allowed.
        branch: Existing branch or None to create a new one.
        branch_kwargs: Additional arguments for branch creation.
        return_branch: If True, return the branch with the selection.
        verbose: Whether to enable verbose output.
        **kwargs: Additional keyword arguments.

    Returns:
        A SelectionModel instance, optionally with the branch.
    """
    if verbose:
        print(f"Starting selection with up to {max_num_selections} choices.")

    branch = branch or Branch(**(branch_kwargs or {}))
    selections, contents = parse_to_representation(choices)
    prompt = PROMPT.format(
        max_num_selections=max_num_selections, choices=selections
    )

    if isinstance(instruct, Instruct):
        instruct = instruct.to_dict()

    instruct = instruct or {}

    if instruct.get("instruction", None) is not None:
        instruct["instruction"] = (
            f"{instruct['instruction']}\n\n{prompt} \n\n "
        )
    else:
        instruct["instruction"] = prompt

    context = instruct.get("context", None) or []
    context = [context] if not isinstance(context, list) else context
    context.extend([{k: v} for k, v in zip(selections, contents)])
    instruct["context"] = context

    response_model: SelectionModel = await branch.operate(
        operative_model=SelectionModel,
        **kwargs,
        **instruct,
    )
    if verbose:
        print(f"Received selection: {response_model.selected}")

    selected = response_model
    if isinstance(response_model, BaseModel) and hasattr(
        response_model, "selected"
    ):
        selected = response_model.selected
    selected = [selected] if not isinstance(selected, list) else selected

    corrected_selections = [parse_selection(i, choices) for i in selected]

    if isinstance(response_model, BaseModel):
        response_model.selected = corrected_selections

    elif isinstance(response_model, dict):
        response_model["selected"] = corrected_selections

    if return_branch:
        return response_model, branch
    return response_model
