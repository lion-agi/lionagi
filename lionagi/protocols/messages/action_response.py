# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, ClassVar

from typing_extensions import override

from lionagi.utils import copy

from ..base import ID
from .action_request import ActionRequest
from .message import MessageFlag, MessageRole, RoledMessage, Template, env


def prepare_action_response_content(
    action_request: ActionRequest,
    output: Any,
) -> dict:
    """
    Prepare the content for an action response.

    Creates a standardized Note object containing the response details and
    maintaining reference to the original request.

    Args:
        action_request: The original action request being responded to
        output: The result from executing the requested function

    Returns:
        Note: Formatted action response content
    """
    return {
        "action_request_id": action_request.id,
        "action_response": {
            "function": action_request.function,
            "arguments": action_request.arguments,
            "output": output,
        },
    }


class ActionResponse(RoledMessage):
    """
    Represents a response to an action request in the system.

    This class encapsulates the result of executing an action request,
    maintaining references to the original request and providing access
    to the execution results.

    Example:
        >>> request = ActionRequest(function="sum", arguments={"nums": [1,2,3]})
        >>> response = ActionResponse(action_request=request, output=6)
        >>> print(response.output)
        6
    """

    template: ClassVar[Template] = env.get_template("action_response.jinja2")

    @override
    def __init__(
        self,
        action_request: ActionRequest,
        output: Any = None,
        protected_init_params: dict | None = None,
    ) -> None:
        """
        Initialize an ActionResponse instance.

        Args:
            action_request: The original action request to respond to
            output: The result from the function execution
            protected_init_params: Protected initialization parameters

        Raises:
            ValueError: If action_request is invalid or already responded to
        """
        message_flags = [
            action_request,
            output,
        ]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            protected_init_params = protected_init_params or {}
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        super().__init__(
            role=MessageRole.ASSISTANT,
            recipient=action_request.sender,
            sender=action_request.recipient,
            content=prepare_action_response_content(
                action_request=action_request,
                output=output,
            ),
        )
        action_request.content["action_response_id"] = self.id

    @property
    def function(self) -> str:
        """
        Get the function name from the action response.

        Returns:
            str: The name of the function that was executed
        """
        return copy(self.content.get(["action_response", "function"]))

    @property
    def arguments(self) -> dict[str, Any]:
        """
        Get the function arguments from the action response.

        Returns:
            dict[str, Any]: The arguments that were used
        """
        return copy(self.content.get(["action_response", "arguments"]))

    @property
    def output(self) -> Any:
        """
        Get the function output from the action response.

        Returns:
            Any: The result returned by the function
        """
        return self.content.get(["action_response", "output"])

    @property
    def response(self) -> dict[str, Any]:
        """
        Get the complete action response as a dictionary.

        Returns:
            dict[str, Any]: The response including function details and output
        """
        return self.content.get("action_response")

    @property
    def action_request_id(self) -> ID[ActionRequest] | None:
        """
        Get the ID of the corresponding action request.

        Returns:
            ID[ActionRequest].ID | None: The ID of the original request
        """
        return copy(self.content.get("action_request_id", None))

    @property
    def rendered(self) -> str:
        return self.template.render(self.content)

    @override
    def _format_content(self) -> dict[str, Any]:
        return {"role": self.role.value, "content": self.rendered}
