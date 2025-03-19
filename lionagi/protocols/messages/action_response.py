# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from typing_extensions import override

from lionagi.protocols.generic.element import IDType
from lionagi.utils import copy

from .action_request import ActionRequest
from .base import MessageRole, SenderRecipient
from .message import RoledMessage, Template, jinja_env


def prepare_action_response_content(
    action_request: ActionRequest,
    output: Any,
) -> dict:
    """
    Convert an ActionRequest + function output into response-friendly dictionary.

    Args:
        action_request (ActionRequest): The original action request.
        output (Any): The result of the function call.

    Returns:
        dict: A dictionary containing `action_request_id` and `action_response`.
    """
    return {
        "action_request_id": str(action_request.id),
        "action_response": {
            "function": action_request.function,
            "arguments": action_request.arguments,
            "output": output,
        },
    }


class ActionResponse(RoledMessage):
    """
    A message fulfilling an `ActionRequest`. It stores the function name,
    the arguments used, and the output produced by the function.
    """

    template: Template | str | None = jinja_env.get_template(
        "action_response.jinja2"
    )

    @property
    def function(self) -> str:
        """Name of the function that was executed."""
        return self.content.get("action_response", {}).get("function", None)

    @property
    def arguments(self) -> dict[str, Any]:
        """Arguments used for the executed function."""
        return self.content.get("action_response", {}).get("arguments", {})

    @property
    def output(self) -> Any:
        """The result or returned data from the function call."""
        return self.content.get("action_response", {}).get("output", None)

    @property
    def response(self) -> dict[str, Any]:
        """
        A helper to get the entire 'action_response' dictionary.

        Returns:
            dict[str, Any]: The entire response, including function, arguments, and output.
        """
        return copy(self.content.get("action_response", {}))

    @property
    def action_request_id(self) -> IDType:
        """The ID of the original action request."""
        return IDType.validate(self.content.get("action_request_id"))

    @override
    @classmethod
    def create(
        cls,
        action_request: ActionRequest,
        output: Any | None = None,
        response_model=None,
        sender: SenderRecipient | None = None,
        recipient: SenderRecipient | None = None,
    ) -> "ActionResponse":
        """
        Build an ActionResponse from a matching `ActionRequest` and output.

        Args:
            action_request (ActionRequest): The original request being fulfilled.
            output (Any, optional): The function output or result.
            response_model (Any, optional):
                If present and has `.output`, this is used instead of `output`.
            sender (SenderRecipient, optional):
                The role or ID of the sender (defaults to the request's recipient).
            recipient (SenderRecipient, optional):
                The role or ID of the recipient (defaults to the request's sender).

        Returns:
            ActionResponse: A new instance referencing the `ActionRequest`.
        """
        if response_model:
            output = response_model.output

        instance = ActionResponse(
            content=prepare_action_response_content(
                action_request=response_model or action_request, output=output
            ),
            role=MessageRole.ACTION,
            sender=sender or action_request.recipient,
            recipient=recipient or action_request.sender,
        )
        action_request.action_response_id = instance.id
        return instance

    def update(
        self,
        action_request: ActionRequest = None,
        output: Any = None,
        response_model=None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        template: Template | str | None = None,
        **kwargs,
    ):
        """
        Update this response with a new request reference or new output.

        Args:
            action_request (ActionRequest): The updated request.
            output (Any): The new function output data.
            response_model: If present, uses response_model.output.
            sender (SenderRecipient): New sender ID or role.
            recipient (SenderRecipient): New recipient ID or role.
            template (Template | str | None): Optional new template.
            **kwargs: Additional fields to store in content.
        """
        if response_model:
            output = response_model.output

        if action_request:
            self.content = prepare_action_response_content(
                action_request=action_request, output=output or self.output
            )
            action_request.action_response_id = self.id
        super().update(
            sender=sender, recipient=recipient, template=template, **kwargs
        )


# File: lionagi/protocols/messages/action_response.py
