# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from typing_extensions import override

from lionagi.protocols.generic.element import IDType
from lionagi.utils import copy

from .action_request import ActionRequest
from .base import MessageRole
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

    template: Template | str = jinja_env.get_template("action_response.jinja")

    @property
    def function(self) -> str:
        """
        Get the function name from the action response.

        Returns:
            str: The name of the function that was executed
        """
        return self.content.get("action_response").get("function")

    @property
    def arguments(self) -> dict[str, Any]:
        """
        Get the function arguments from the action response.

        Returns:
            dict[str, Any]: The arguments that were used
        """
        return self.content.get("action_response").get("arguments")

    @property
    def output(self) -> Any:
        """
        Get the function output from the action response.

        Returns:
            Any: The result returned by the function
        """
        return self.content.get("action_response").get("output")

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
        output: Any,
    ):
        return ActionRequest(
            content=prepare_action_response_content(
                action_request=action_request, output=output
            ),
            role=MessageRole.ACTION,
            sender=action_request.recipient,
            recipient=action_request.sender,
        )
