# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
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
    return {
        "action_request_id": str(action_request.id),
        "action_response": {
            "function": action_request.function,
            "arguments": action_request.arguments,
            "output": output,
        },
    }


class ActionResponse(RoledMessage):

    template: Template | str | None = jinja_env.get_template(
        "action_response.jinja2"
    )

    @property
    def function(self) -> str:
        """
        Get the function name from the action response.

        Returns:
            str: The name of the function that was executed
        """
        return self.content.get("action_response", {}).get("function", None)

    @property
    def arguments(self) -> dict[str, Any]:
        """
        Get the function arguments from the action response.

        Returns:
            dict[str, Any]: The arguments that were used
        """
        return self.content.get("action_response", {}).get("arguments", {})

    @property
    def output(self) -> Any:
        """
        Get the function output from the action response.

        Returns:
            Any: The result returned by the function
        """
        return self.content.get("action_response", {}).get("output", None)

    @property
    def response(self) -> dict[str, Any]:
        """
        Get the complete action response as a dictionary.

        Returns:
            dict[str, Any]: The response including function details and output
        """
        return copy(self.content.get("action_response", {}))

    @property
    def action_request_id(self) -> IDType:
        """
        Get the ID of the corresponding action request.

        Returns:
            ID[ActionRequest].ID | None: The ID of the original request
        """
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
