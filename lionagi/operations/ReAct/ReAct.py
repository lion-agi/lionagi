# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from lionagi.operatives.types import Instruct
from lionagi.service.imodel import iModel
from lionagi.utils import copy

from .utils import ReActAnalysis

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def ReAct(
    branch: "Branch",
    instruct: Instruct | dict[str, Any],
    interpret: bool = False,
    interpret_domain: str | None = None,
    interpret_style: str | None = None,
    interpret_sample: str | None = None,
    interpret_kwargs: dict | None = None,
    tools: Any = None,
    tool_schemas: Any = None,
    response_format: type[BaseModel] | BaseModel = None,
    extension_allowed: bool = False,
    max_extensions: int | None = None,
    response_kwargs: dict | None = None,
    return_analysis: bool = False,
    analysis_model: iModel | None = None,
    verbose_analysis: bool = False,
    **kwargs,
):
    # If no tools or tool schemas are provided, default to "all tools"
    if not tools and not tool_schemas:
        tools = True

    # Possibly interpret the instruction to refine it
    instruction_str = None
    if interpret:
        instruction_str = await branch.interpret(
            str(
                instruct.to_dict()
                if isinstance(instruct, Instruct)
                else instruct
            ),
            domain=interpret_domain,
            style=interpret_style,
            sample_writing=interpret_sample,
            **(interpret_kwargs or {}),
        )

    # Convert Instruct to dict if necessary
    instruct_dict = (
        instruct.to_dict()
        if isinstance(instruct, Instruct)
        else dict(instruct)
    )

    # Overwrite "instruction" with the interpreted prompt (if any) plus a note about expansions
    max_ext_info = f"\nIf needed, you can do up to {max_extensions or 0 if extension_allowed else 0} expansions."
    instruct_dict["instruction"] = (
        instruction_str
        or (instruct_dict.get("instruction") or "")  # in case it's missing
    ) + max_ext_info

    # Prepare a copy of user-provided kwargs for the first operate call
    kwargs_for_operate = copy(kwargs)
    kwargs_for_operate["actions"] = True
    kwargs_for_operate["reason"] = True

    # Step 1: Generate initial ReAct analysis
    analysis: ReActAnalysis = await branch.operate(
        instruct=instruct_dict,
        response_format=ReActAnalysis,
        tools=tools,
        tool_schemas=tool_schemas,
        chat_model=analysis_model or branch.chat_model,
        **kwargs_for_operate,
    )
    analyses = [analysis]

    # If verbose, show round #1 analysis
    if verbose_analysis:
        print(
            f"ReAct Round #1 Analysis:\n {analysis.model_dump_json(indent=2)}",
        )

    # Validate and clamp max_extensions if needed
    if max_extensions and max_extensions > 5:
        logging.warning("max_extensions should not exceed 5; defaulting to 5.")
        max_extensions = 5

    # Step 2: Possibly loop through expansions if extension_needed
    extensions = max_extensions
    round_count = 1

    while (
        extension_allowed
        and analysis.extension_needed
        and (extensions if max_extensions else 0) > 0
    ):
        new_instruction = None
        if extensions == max_extensions:
            new_instruction = ReActAnalysis.FIRST_EXT_PROMPT.format(
                extensions=extensions
            )
        else:
            new_instruction = ReActAnalysis.CONTINUE_EXT_PROMPT.format(
                extensions=extensions
            )

        operate_kwargs = copy(kwargs)
        operate_kwargs["actions"] = True
        operate_kwargs["reason"] = True
        operate_kwargs["response_format"] = ReActAnalysis
        operate_kwargs["action_strategy"] = analysis.action_strategy
        if analysis.action_batch_size:
            operate_kwargs["action_batch_size"] = analysis.action_batch_size

        analysis = await branch.operate(
            instruction=new_instruction,
            tools=tools,
            tool_schemas=tool_schemas,
            **operate_kwargs,
        )
        analyses.append(analysis)
        round_count += 1

        # If verbose, show round analysis
        if verbose_analysis:
            print(
                f"ReAct Round #{round_count} Analysis:\n {analysis.model_dump_json(indent=2)}",
            )
        if extensions:
            extensions -= 1

    # Step 3: Produce final answer by calling branch.instruct with an answer prompt
    answer_prompt = ReActAnalysis.ANSWER_PROMPT.format(
        instruction=instruct_dict["instruction"]
    )
    out = await branch.communicate(
        instruction=answer_prompt,
        response_format=response_format,
        **(response_kwargs or {}),
    )
    if return_analysis:
        return out, analyses
    return out
