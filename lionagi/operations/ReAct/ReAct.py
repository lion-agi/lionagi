# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

from lionagi.libs.schema.as_readable import as_readable
from lionagi.libs.validate.common_field_validators import (
    validate_model_to_type,
)
from lionagi.operatives.models.field_model import FieldModel
from lionagi.operatives.models.model_params import ModelParams
from lionagi.operatives.types import Instruct
from lionagi.service.imodel import iModel
from lionagi.utils import copy

from .utils import Analysis, ReActAnalysis

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def ReAct(
    branch: "Branch",
    instruct: Instruct | dict[str, Any],
    interpret: bool = False,
    interpret_domain: str | None = None,
    interpret_style: str | None = None,
    interpret_sample: str | None = None,
    interpret_model: str | None = None,
    interpret_kwargs: dict | None = None,
    tools: Any = None,
    tool_schemas: Any = None,
    response_format: type[BaseModel] | BaseModel = None,
    intermediate_response_options: list[BaseModel] | BaseModel = None,
    intermediate_listable: bool = False,
    reasoning_effort: Literal["low", "medium", "high"] = None,
    extension_allowed: bool = True,
    max_extensions: int | None = 3,
    response_kwargs: dict | None = None,
    display_as: Literal["json", "yaml"] = "yaml",
    return_analysis: bool = False,
    analysis_model: iModel | None = None,
    verbose_analysis: bool = False,
    verbose_length: int = None,
    include_token_usage_to_model: bool = True,
    continue_after_failed_response: bool = False,
    **kwargs,
):
    outs = []
    if verbose_analysis:
        async for i in ReActStream(
            branch=branch,
            instruct=instruct,
            interpret=interpret,
            interpret_domain=interpret_domain,
            interpret_style=interpret_style,
            interpret_sample=interpret_sample,
            interpret_model=interpret_model,
            interpret_kwargs=interpret_kwargs,
            tools=tools,
            tool_schemas=tool_schemas,
            response_format=response_format,
            intermediate_response_options=intermediate_response_options,
            intermediate_listable=intermediate_listable,
            reasoning_effort=reasoning_effort,
            extension_allowed=extension_allowed,
            max_extensions=max_extensions,
            response_kwargs=response_kwargs,
            analysis_model=analysis_model,
            verbose_analysis=verbose_analysis,
            display_as=display_as,
            verbose_length=verbose_length,
            include_token_usage_to_model=include_token_usage_to_model,
            continue_after_failed_response=continue_after_failed_response,
            **kwargs,
        ):
            analysis, str_ = i
            str_ += "\n---------\n"
            as_readable(str_, md=True, display_str=True)
            outs.append(analysis)
    else:
        async for i in ReActStream(
            branch=branch,
            instruct=instruct,
            interpret=interpret,
            interpret_domain=interpret_domain,
            interpret_style=interpret_style,
            interpret_sample=interpret_sample,
            interpret_model=interpret_model,
            interpret_kwargs=interpret_kwargs,
            tools=tools,
            tool_schemas=tool_schemas,
            response_format=response_format,
            intermediate_response_options=intermediate_response_options,
            intermediate_listable=intermediate_listable,
            reasoning_effort=reasoning_effort,
            extension_allowed=extension_allowed,
            max_extensions=max_extensions,
            response_kwargs=response_kwargs,
            analysis_model=analysis_model,
            display_as=display_as,
            verbose_length=verbose_length,
            include_token_usage_to_model=include_token_usage_to_model,
            continue_after_failed_response=continue_after_failed_response,
            **kwargs,
        ):
            outs.append(i)
    if return_analysis:
        return outs
    return outs[-1]


async def ReActStream(
    branch: "Branch",
    instruct: Instruct | dict[str, Any],
    interpret: bool = False,
    interpret_domain: str | None = None,
    interpret_style: str | None = None,
    interpret_sample: str | None = None,
    interpret_model: str | None = None,
    interpret_kwargs: dict | None = None,
    tools: Any = None,
    tool_schemas: Any = None,
    response_format: type[BaseModel] | BaseModel = None,
    intermediate_response_options: list[BaseModel] | BaseModel = None,
    intermediate_listable: bool = False,
    reasoning_effort: Literal["low", "medium", "high"] = None,
    extension_allowed: bool = True,
    max_extensions: int | None = 3,
    response_kwargs: dict | None = None,
    analysis_model: iModel | None = None,
    verbose_analysis: bool = False,
    display_as: Literal["json", "yaml"] = "yaml",
    verbose_length: int = None,
    include_token_usage_to_model: bool = True,
    continue_after_failed_response: bool = False,
    **kwargs,
) -> AsyncGenerator:
    irfm: FieldModel | None = None

    if intermediate_response_options is not None:
        iro = (
            [intermediate_response_options]
            if not isinstance(intermediate_response_options, list)
            else intermediate_response_options
        )
        field_models = []
        for i in iro:
            type_ = validate_model_to_type(None, i)
            fm = FieldModel(
                name=str(type_.__name__).lower(),
                annotation=type_ | None,
                validator=lambda cls, x: None if x == {} else x,
            )
            field_models.append(fm)

        m_ = ModelParams(
            name="IntermediateResponseOptions", field_models=field_models
        ).create_new_model()

        irfm = FieldModel(
            name="intermediate_response_options",
            annotation=(
                m_ | None if not intermediate_listable else list[m_] | None
            ),
            description="Optional intermediate deliverable outputs. fill as needed ",
            validator=lambda cls, x: None if not x else x,
        )

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
            interpret_model=interpret_model,
            **(interpret_kwargs or {}),
        )
        if verbose_analysis:
            str_ = "\n### Interpreted instruction:\n"
            str_ += as_readable(
                instruction_str,
                md=True,
                format_curly=True if display_as == "yaml" else False,
                max_chars=verbose_length,
            )
            yield instruction_str, str_
        else:
            yield instruction_str

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
    kwargs_for_operate["include_token_usage_to_model"] = (
        include_token_usage_to_model
    )

    # Step 1: Generate initial ReAct analysis
    analysis: ReActAnalysis = await branch.operate(
        instruct=instruct_dict,
        response_format=ReActAnalysis,
        tools=tools,
        tool_schemas=tool_schemas,
        chat_model=analysis_model or branch.chat_model,
        **kwargs_for_operate,
    )
    # If verbose, show round #1 analysis
    if verbose_analysis:
        str_ = "\n### ReAct Round No.1 Analysis:\n"
        str_ += as_readable(
            analysis,
            md=True,
            format_curly=True if display_as == "yaml" else False,
            max_chars=verbose_length,
        )
        yield analysis, str_
    else:
        yield analysis

    # Validate and clamp max_extensions if needed
    if max_extensions and max_extensions > 100:
        logging.warning(
            "max_extensions should not exceed 100; defaulting to 100."
        )
        max_extensions = 100

    # Step 2: Possibly loop through expansions if extension_needed
    extensions = max_extensions
    round_count = 1

    while (
        extension_allowed and analysis.extension_needed
        if hasattr(analysis, "extension_needed")
        else (
            analysis.get("extension_needed", None)
            if isinstance(analysis, dict)
            else False
        )
        and (extensions - 1 if max_extensions else 0) > 0
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
        operate_kwargs["include_token_usage_to_model"] = (
            include_token_usage_to_model
        )
        if analysis.action_batch_size:
            operate_kwargs["action_batch_size"] = analysis.action_batch_size
        if irfm:
            operate_kwargs["field_models"] = operate_kwargs.get(
                "field_models", []
            ) + [irfm]
        if reasoning_effort:
            guide = None
            if reasoning_effort == "low":
                guide = "Quick concise reasoning.\n"
            if reasoning_effort == "medium":
                guide = "Reasonably balanced reasoning.\n"
            if reasoning_effort == "high":
                guide = "Thorough, try as hard as you can in reasoning.\n"
            operate_kwargs["guidance"] = guide + operate_kwargs.get(
                "guidance", ""
            )
            operate_kwargs["reasoning_effort"] = reasoning_effort

        analysis = await branch.operate(
            instruction=new_instruction,
            tools=tools,
            tool_schemas=tool_schemas,
            **operate_kwargs,
        )
        round_count += 1

        if isinstance(analysis, dict) and all(
            i is None for i in analysis.values()
        ):
            if not continue_after_failed_response:
                raise ValueError(
                    "All values in the response are None. "
                    "This might be due to a failed response. "
                    "Set `continue_after_failed_response=True` to ignore this error."
                )

        # If verbose, show round analysis
        if verbose_analysis:
            str_ = f"\n### ReAct Round No.{round_count} Analysis:\n"

            str_ += as_readable(
                analysis,
                md=True,
                format_curly=True if display_as == "yaml" else False,
                max_chars=verbose_length,
            )

            yield analysis, str_
        else:
            yield analysis

        if extensions:
            extensions -= 1

    # Step 3: Produce final answer by calling branch.instruct with an answer prompt
    answer_prompt = ReActAnalysis.ANSWER_PROMPT.format(
        instruction=instruct_dict["instruction"]
    )
    if not response_format:
        response_format = Analysis

    try:
        out = await branch.operate(
            instruction=answer_prompt,
            response_format=response_format,
            **(response_kwargs or {}),
        )
        if isinstance(analysis, dict) and all(
            i is None for i in analysis.values()
        ):
            if not continue_after_failed_response:
                raise ValueError(
                    "All values in the response are None. "
                    "This might be due to a failed response. "
                    "Set `continue_after_failed_response=True` to ignore this error."
                )
    except Exception:
        out = branch.msgs.last_response.response

    if isinstance(out, Analysis):
        out = out.answer

    if verbose_analysis:
        str_ = "\n### ReAct Final Answer:\n"
        str_ += as_readable(
            out,
            md=True,
            format_curly=True if display_as == "yaml" else False,
            max_chars=verbose_length,
        )
        yield out, str_
    else:
        yield out


# TODO: Do partial intermeditate output for longer analysis with form and report
