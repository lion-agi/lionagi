# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, JsonValue

from lionagi.operatives.types import (
    FieldModel,
    Instruct,
    ModelParams,
    Operative,
    Step,
    ToolRef,
)
from lionagi.protocols.types import Instruction, Progression, SenderRecipient
from lionagi.service.imodel import iModel

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def operate(
    branch: "Branch",
    *,
    instruct: Instruct = None,
    instruction: Instruction | JsonValue = None,
    guidance: JsonValue = None,
    context: JsonValue = None,
    sender: SenderRecipient = None,
    recipient: SenderRecipient = None,
    progression: Progression = None,
    imodel: iModel = None,  # deprecated, alias of chat_model
    chat_model: iModel = None,
    invoke_actions: bool = True,
    tool_schemas: list[dict] = None,
    images: list = None,
    image_detail: Literal["low", "high", "auto"] = None,
    parse_model: iModel = None,
    skip_validation: bool = False,
    tools: ToolRef = None,
    operative: Operative = None,
    response_format: type[BaseModel] = None,  # alias of operative.request_type
    return_operative: bool = False,
    actions: bool = False,
    reason: bool = False,
    action_kwargs: dict = None,
    action_strategy: Literal[
        "sequential", "concurrent", "batch"
    ] = "concurrent",
    action_batch_size: int = None,
    verbose_action: bool = False,
    field_models: list[FieldModel] = None,
    exclude_fields: list | dict | None = None,
    request_params: ModelParams = None,
    request_param_kwargs: dict = None,
    response_params: ModelParams = None,
    response_param_kwargs: dict = None,
    handle_validation: Literal[
        "raise", "return_value", "return_none"
    ] = "return_value",
    operative_model: type[BaseModel] = None,
    request_model: type[BaseModel] = None,
    include_token_usage_to_model: bool = False,
    **kwargs,
) -> list | BaseModel | None | dict | str:
    if operative_model:
        logging.warning(
            "`operative_model` is deprecated. Use `response_format` instead."
        )
    if (
        (operative_model and response_format)
        or (operative_model and request_model)
        or (response_format and request_model)
    ):
        raise ValueError(
            "Cannot specify both `operative_model` and `response_format` (or `request_model`) "
            "as they are aliases of each other."
        )

    # Use the final chosen format
    response_format = response_format or operative_model or request_model

    # Decide which chat model to use
    chat_model = chat_model or imodel or branch.chat_model
    parse_model = parse_model or chat_model

    # Convert dict-based instructions to Instruct if needed
    if isinstance(instruct, dict):
        instruct = Instruct(**instruct)

    # Or create a new Instruct if not provided
    instruct = instruct or Instruct(
        instruction=instruction,
        guidance=guidance,
        context=context,
    )

    # If reason or actions are requested, apply them to instruct
    if reason:
        instruct.reason = True
    if actions:
        instruct.actions = True
        if action_strategy:
            instruct.action_strategy = action_strategy

    # 1) Create or update the Operative
    operative = Step.request_operative(
        request_params=request_params,
        reason=instruct.reason,
        actions=instruct.actions,
        exclude_fields=exclude_fields,
        base_type=response_format,
        field_models=field_models,
        **(request_param_kwargs or {}),
    )

    # If the instruction signals actions, ensure tools are provided
    if instruct.actions:
        tools = tools or True

    # If we want to auto-invoke tools, fetch or generate the schemas
    if invoke_actions and tools:
        tool_schemas = tool_schemas or branch.acts.get_tool_schema(tools=tools)

    # 2) Send the instruction to the chat model
    ins, res = await branch.chat(
        instruction=instruct.instruction,
        guidance=instruct.guidance,
        context=instruct.context,
        sender=sender,
        recipient=recipient,
        response_format=operative.request_type,
        progression=progression,
        imodel=chat_model,  # or the override
        images=images,
        image_detail=image_detail,
        tool_schemas=tool_schemas,
        return_ins_res_message=True,
        include_token_usage_to_model=include_token_usage_to_model,
        **kwargs,
    )
    branch.msgs.add_message(instruction=ins)
    branch.msgs.add_message(assistant_response=res)

    # 3) Populate the operative with the raw response
    operative.response_str_dict = res.response

    # 4) Possibly skip validation
    if skip_validation:
        return operative if return_operative else operative.response_str_dict

    # 5) Parse or validate the response into the operative's model
    response_model = operative.update_response_model(res.response)
    if not isinstance(response_model, BaseModel):
        # If the response isn't directly a model, attempt a parse
        response_model = await branch.parse(
            text=res.response,
            request_type=operative.request_type,
            max_retries=operative.max_retries,
            handle_validation="return_value",
        )
        operative.response_model = operative.update_response_model(
            text=response_model
        )

    # If we still fail to parse, handle according to user preference
    if not isinstance(response_model, BaseModel):
        match handle_validation:
            case "return_value":
                return response_model
            case "return_none":
                return None
            case "raise":
                raise ValueError(
                    "Failed to parse the LLM response into the requested format."
                )

    # 6) If no tool invocation is needed, return result or operative
    if not invoke_actions:
        return operative if return_operative else operative.response_model

    # 7) If the model indicates an action is required, call the tools
    if (
        getattr(response_model, "action_required", None) is True
        and getattr(response_model, "action_requests", None) is not None
    ):
        action_kwargs = action_kwargs or {}
        action_kwargs["strategy"] = (
            instruct.action_strategy
            if instruct.action_strategy
            else action_kwargs.get("strategy", "concurrent")
        )
        if action_batch_size:
            action_kwargs["batch_size"] = action_batch_size

        action_response_models = await branch.act(
            response_model.action_requests,
            verbose_action=verbose_action,
            **action_kwargs,
        )
        # Possibly refine the operative with the tool outputs
        operative = Step.respond_operative(
            response_params=response_params,
            operative=operative,
            additional_data={"action_responses": action_response_models},
            **(response_param_kwargs or {}),
        )

    # Return final result or the full operative
    return operative if return_operative else operative.response_model
