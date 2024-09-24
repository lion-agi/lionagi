"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Module for parallel processing of direct interactions in the Lion framework.

This module provides functionality to handle multiple direct processes
concurrently across different branches of a session.
"""

import asyncio
from functools import partial
from typing import Any, Tuple

from lion_core.session.session import Session
from lionagi.core.report.base import BaseForm
from lion_core.session.branch import Branch
from lion_core.generic.pile import pile, Pile
from lion_core.libs import to_list
from lionagi.core.unit.unit import Unit

as_nice_list = partial(to_list, flatten=True, dropna=True)


async def process_parallel_direct(
    session: Session,
    *,
    branches: Pile[Branch] = None,
    form: BaseForm | None = None,
    instruction: str | None = None,
    context: dict[str, Any] | None = None,
    tools: Any | None = None,
    reason: bool = True,
    predict: bool = False,
    score: bool = True,
    select: Any | None = None,
    plan: Any | None = None,
    brainstorm: Any | None = None,
    reflect: Any | None = None,
    tool_schema: Any | None = None,
    allow_action: bool = False,
    allow_extension: bool = False,
    max_extension: int | None = None,
    confidence: Any | None = None,
    score_num_digits: int | None = None,
    score_range: Tuple[float, float] | None = None,
    select_choices: list[str] | None = None,
    plan_num_step: int | None = None,
    predict_num_sentences: int | None = None,
    clear_messages: bool = False,
    verbose_direct: bool = True,
    images: str | list[str] | None = None,
    imodel=None,
    tool_manager=None,
    num_instances: int = 1,
    image_path: str | None = None,
    branch_system: Any = None,
    branch_system_datetime: Any = None,
    branch_messages=None,
    explode: bool = False,
    **kwargs: Any,
) -> list[Any]:
    """
    Process direct interactions in parallel across multiple branches.

    Args:
        session: The Session object to process direct interactions for.
        branches: Existing branches to use for processing.
        form: The form associated with the direct interaction.
        instruction: Instruction(s) for the direct interaction (single or list).
        context: Context(s) for the direct interaction (single or list).
        tools: Tools configuration for the branches.
        reason, predict, score, select, plan, brainstorm, reflect: Direct
            interaction parameters.
        tool_schema: Schema for tools.
        allow_action, allow_extension: Flags for action and extension allowance.
        max_extension: Maximum number of extensions allowed.
        confidence, score_num_digits, score_range: Scoring parameters.
        select_choices: Choices for selection tasks.
        plan_num_step: Number of steps for planning tasks.
        predict_num_sentences: Number of sentences for prediction tasks.
        clear_messages: Whether to clear existing branch messages.
        verbose_direct: Whether to use verbose mode for direct interactions.
        images: Image data for the direct interaction.
        imodel: The iModel to use for completion.
        tool_manager: Tool manager for new branches.
        num_instances: Number of instances to create for each combination.
        image_path: Path to image file.
        branch_system: System message for new branches.
        branch_system_datetime: Datetime for system messages in new branches.
        branch_messages: Initial messages for new branches.
        explode: Whether to create all possible instruction-context pairs.
        **kwargs: Additional keyword arguments for direct processing.

    Returns:
        A list of results from parallel direct processing.
    """
    branches = branches or pile()

    async def process_single_direct(branch_, instruct_, context_):
        if not branch_:
            branch_ = await session.new_branch(
                system=branch_system,
                system_sender=session.ln_id,
                system_datetime=branch_system_datetime,
                user=session.user,
                imodel=imodel or session.imodel,
                messages=branch_messages,
                tool_manager=tool_manager,
                tools=tools,
            )

        unit_ = Unit(branch=branch_)
        resp_ = await unit_.process_direct(
            instruction=instruct_,
            context=context_,
            form=form,
            reason=reason,
            predict=predict,
            score=score,
            select=select,
            plan=plan,
            brainstorm=brainstorm,
            reflect=reflect,
            tool_schema=tool_schema,
            allow_action=allow_action,
            allow_extension=allow_extension,
            max_extension=max_extension,
            confidence=confidence,
            score_num_digits=score_num_digits,
            score_range=score_range,
            select_choices=select_choices,
            plan_num_step=plan_num_step,
            predict_num_sentences=predict_num_sentences,
            clear_messages=clear_messages,
            verbose_direct=verbose_direct,
            images=images,
            image_path=image_path,
            **kwargs,
        )
        branches.include(branch_)
        return resp_

    async def process_multiple_instances(branch, instruct_=None, context_=None):
        tasks = [
            process_single_direct(branch, instruct_, context_)
            for _ in range(num_instances)
        ]
        return as_nice_list(await asyncio.gather(*tasks))

    async def process_multi_instruction(branch):
        tasks = [
            process_multiple_instances(branch, instruct_=ins_)
            for ins_ in as_nice_list(instruction)
        ]
        return as_nice_list(await asyncio.gather(*tasks))

    async def process_multi_context(branch):
        tasks = [
            process_multiple_instances(branch, context_=ctx_)
            for ctx_ in as_nice_list(context)
        ]
        return as_nice_list(await asyncio.gather(*tasks))

    async def process_multi_instruction_context(branch):
        if explode:
            tasks = [
                process_multiple_instances(branch, instruct_=ins_, context_=ctx_)
                for ins_ in as_nice_list(instruction)
                for ctx_ in as_nice_list(context)
            ]
        else:
            tasks = [
                process_multiple_instances(branch, instruct_=ins_, context_=ctx_)
                for ins_, ctx_ in zip(as_nice_list(instruction), as_nice_list(context))
            ]
        return as_nice_list(await asyncio.gather(*tasks))

    instr_list = as_nice_list(instruction)
    ctx_list = as_nice_list(context)

    if len(instr_list) == 1:
        if len(ctx_list) == 1:
            out_ = await process_multiple_instances(0)
        else:
            out_ = await process_multi_context(0)
    elif len(ctx_list) == 1:
        out_ = await process_multi_instruction(0)
    else:
        out_ = await process_multi_instruction_context(0)

    session.branches.include(list(branches))
    return out_


__all__ = ["process_parallel_direct"]

# File: lion_core/direct/parallel_processing.py
