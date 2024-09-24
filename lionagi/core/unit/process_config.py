"""Module for processing chat configurations in the Lion framework."""

from typing import Any, Literal

from lion_core.abc import Observable
from lion_core.form.base import BaseForm
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.message import MessageFlag
from lion_core.communication.instruction import Instruction

from lion_core.session.branch import Branch


def process_chat_config(
    branch: "Branch",
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
    **kwargs: Any,  # additional model parameters
) -> dict:
    """
    Process chat configuration for a branch in the Lion framework.

    Args:
        branch: The Branch instance to process the configuration for.
        instruction: The instruction for the chat (priority 2).
        context: Additional context for the chat.
        form: The BaseForm instance to use (priority 1).
        sender: The sender of the message.
        system_sender: The system sender.
        recipient: The recipient of the message.
        request_fields: Fields requested in the response.
        system: System message content.
        guidance: Guidance for the chat.
        strict_form: Whether to use strict form validation.
        action_request: An ActionRequest object.
        images: List of images related to the message.
        image_detail: Level of detail for image processing.
        system_datetime: Datetime for system messages.
        metadata: Additional metadata for the message.
        delete_previous_system: Whether to delete the previous system message.
        tools: Whether to include tools in the configuration.
        system_metadata: Metadata for the system message.
        model_config: Configuration for the model.
        assignment: Assignment string for the form.
        task_description: Description of the task.
        fill_inputs: Whether to fill input fields.
        none_as_valid_value: Whether to treat None as a valid value.
        input_fields_value_kwargs: Keyword arguments for input field values.
        **kwargs: Additional keyword arguments for model parameters.

    Returns:
        A dictionary containing the processed chat configuration.
    """
    message_kwargs = {
        "context": context,
        "sender": sender,
        "recipient": recipient,
        "images": images,
        "image_detail": image_detail,
        "metadata": metadata,
        "action_request": action_request,
        "guidance": guidance,
        "request_fields": request_fields,
    }

    if form:
        message_kwargs["instruction"] = Instruction.from_form(
            form=form,
            sender=sender,
            recipient=recipient,
            images=images,
            image_detail=image_detail,
            strict=strict_form,
            assignment=assignment,
            task_description=task_description,
            fill_inputs=fill_inputs,
            input_value_kwargs=input_fields_value_kwargs,
            none_as_valid_value=none_as_valid_value,
        )

    else:
        message_kwargs["instruction"] = instruction

    if system:
        branch.add_message(
            system=system,
            system_datetime=system_datetime,
            delete_previous_system=delete_previous_system,
            system_sender=system_sender,
            metadata=system_metadata,
        )

    branch.add_message(**message_kwargs)

    config = model_config or {}
    config.update(kwargs)

    if "tool_parsed" in config:
        config.pop("tool_parsed")
        config["tools"] = tools
    elif tools and branch.has_tools:
        config.update(
            branch.tool_manager.get_tool_schema(tools=tools),
        )

    if sender is not None:
        config["sender"] = sender

    return config


__all__ = ["process_chat_config"]

# File: lion_core/chat/process_config.py
