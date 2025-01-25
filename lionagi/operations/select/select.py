# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from lionagi.operatives.types import Instruct

from .utils import SelectionModel

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def select(
    branch: "Branch",
    instruct: Instruct | dict[str, Any],
    choices: list[str] | type[Enum] | dict[str, Any],
    max_num_selections: int = 1,
    branch_kwargs: dict[str, Any] | None = None,
    return_branch: bool = False,
    verbose: bool = False,
    **kwargs: Any,
) -> SelectionModel | tuple[SelectionModel, "Branch"]:
    if verbose:
        print(f"Starting selection with up to {max_num_selections} choices.")

    from .utils import SelectionModel, parse_selection, parse_to_representation

    branch = branch or Branch(**(branch_kwargs or {}))
    selections, contents = parse_to_representation(choices)
    prompt = SelectionModel.PROMPT.format(
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
        response_format=SelectionModel,
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
