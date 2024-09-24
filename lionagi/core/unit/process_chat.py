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
Module for processing chat interactions in the Lion framework.

This module provides the main function for handling chat processing,
including configuration, completion, action requests, and validation.
"""

from typing import Any, Callable, Literal

from lionagi import iModel

from lion_core.generic.progression import Progression


from lion_core.communication.action_request import ActionRequest
from lion_core.rule.rulebook import RuleBook
from lion_core.rule.rule_processor import RuleProcessor
from lionagi.core.unit.process_config import process_chat_config
from lionagi.core.unit.process_completion import (
    process_chatcompletion,
    process_model_response,
)
from lionagi.core.unit.process_action_request import process_action_request
from lionagi.core.unit.process_rule import process_rule
from lion_core.session.branch import Branch

from lion_core.abc import Observable
from lion_core.form.base import BaseForm
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.message import MessageFlag
from lionagi.core.unit.process_action_response import process_action_response


async def process_chat(
    branch: Branch,
    *,
    instruction: Any = None,  # priority 2
    context: Any = None,
    form: BaseForm | None = None,  # priority 1
    sender: Observable | str | None = None,
    system_sender=None,
    recipient: Observable | str | None = None,
    request_fields: dict | MessageFlag | None = None,
    system: Any = None,
    guidance: Any = None,
    strict_form: bool = False,
    action_request: ActionRequest | None = None,
    images: list | MessageFlag | None = None,
    image_detail: Literal["low", "high", "auto"] | MessageFlag | None = None,
    system_datetime: bool | str | MessageFlag | None = None,
    metadata: Any = None,
    delete_previous_system: bool = False,
    tools: bool | None = None,
    system_metadata: Any = None,
    model_config: dict | None = None,
    assignment: str = None,  # if use form, must provide assignment
    task_description: str = None,
    fill_inputs: bool = True,
    none_as_valid_value: bool = False,
    input_fields_value_kwargs: dict = None,
    clear_messages: bool = False,
    imodel: iModel = None,
    progress: Progression = None,
    costs=(0, 0),
    fill_value: Any = None,
    fill_mapping: dict = None,
    response_parser: Callable = None,
    response_parser_kwargs: dict = None,
    handle_unmatched="ignore",
    rule_processor: RuleProcessor = None,
    rulebook: RuleBook = None,
    strict_validation=None,
    return_branch: bool = False,
    structure_str: bool = False,
    fallback_structure: Callable = None,
    **kwargs: Any,  # additional model parameters
):

    if clear_messages:
        branch.clear_messages()

    config = process_chat_config(
        system_sender=system_sender,
        branch=branch,
        instruction=instruction,
        context=context,
        form=form,
        sender=sender,
        recipient=recipient,
        request_fields=request_fields,
        system=system,
        guidance=guidance,
        strict_form=strict_form,
        action_request=action_request,
        images=images,
        image_detail=image_detail,
        system_datetime=system_datetime,
        metadata=metadata,
        delete_previous_system=delete_previous_system,
        tools=tools,
        system_metadata=system_metadata,
        model_config=model_config,
        assignment=assignment,
        task_description=task_description,
        fill_inputs=fill_inputs,
        none_as_valid_value=none_as_valid_value,
        input_fields_value_kwargs=input_fields_value_kwargs,
        **kwargs,
    )
    imodel: iModel = imodel or branch.imodel
    payload, completion = await imodel.chat(
        branch.to_chat_messages(progress=progress),
        **config,
    )

    message = await process_chatcompletion(
        branch=branch,
        imodel=imodel,
        payload=payload,
        completion=completion,
        sender=sender,
        costs=costs,
    )

    if message is None:
        return None

    response: dict | str = process_model_response(
        content_=message,
        request_fields=request_fields,
        fill_value=fill_value,
        fill_mapping=fill_mapping,
        strict=False,
        handle_unmatched=handle_unmatched,
    )

    action_requests, action_outputs = await process_action_request(
        branch=branch,
        response=response,
        action_request=action_request,
    )

    await process_action_response(
        branch=branch,
        action_requests=action_requests,
        responses=action_outputs,
        response_parser=response_parser,
        parser_kwargs=response_parser_kwargs,
    )

    if form:
        form = await process_rule(
            form=form,
            rule_processor=rule_processor,
            response_=response,
            rulebook=rulebook,
            strict=strict_validation,
            structure_str=structure_str,
            fallback_structure=fallback_structure,
        )
        return branch, form if return_branch else form

    return branch, response if return_branch else response


__all__ = ["process_chat"]

# File: lion_core/chat/processing.py
