# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from typing import Any

from lionagi.utils import copy, to_dict

from ..generic.element import IDType
from .base import SenderRecipient
from .message import MessageRole, RoledMessage, Template, jinja_env


def prepare_action_request(
    function: str | Callable,
    arguments: dict,
) -> dict[str, Any]:

    if isinstance(function, Callable):
        function = function.__name__
    if hasattr(function, "function"):
        function = function.function
    if not isinstance(function, str):
        raise ValueError("Function must be a string or callable.")

    arguments = copy(arguments)
    if not isinstance(arguments, dict):
        try:
            arguments = to_dict(arguments, fuzzy_parse=True)
            if isinstance(arguments, list | tuple) and len(arguments) > 0:
                arguments = arguments[0]
        except Exception:
            raise ValueError("Arguments must be a dictionary.")
    return {"action_request": {"function": function, "arguments": arguments}}


class ActionRequest(RoledMessage):

    template: Template | str | None = jinja_env.get_template(
        "action_request.jinja2"
    )

    @property
    def action_response_id(self) -> IDType | None:
        """
        Get the ID of the corresponding action response.

        Returns:
            IDType | None: The ID of the action response, or None if not responded
        """
        return self.content.get("action_response_id", None)

    @action_response_id.setter
    def action_response_id(self, action_response_id: IDType) -> None:
        """
        Set the ID of the corresponding action response.

        Args:
            action_response_id: The ID of the action response
        """
        self.content["action_response_id"] = action_response_id

    @property
    def request(self) -> dict[str, Any]:
        """
        Get the action request content as a dictionary.

        Returns:
            dict[str, Any]: The request content excluding output
        """
        return copy(self.content.get("action_request", {}))

    @property
    def arguments(self) -> dict[str, Any]:
        """
        Get the arguments for the action request.

        Returns:
            dict[str, Any]: The arguments dictionary
        """
        return self.request.get("arguments", {})

    @property
    def function(self) -> str:
        """
        Get the function name for the action request.

        Returns:
            str: The name of the function to be invoked
        """
        return self.request.get("function", "")

    @classmethod
    def create(
        cls,
        function=None,
        arguments: dict | None = None,
        sender: SenderRecipient | None = None,
        recipient: SenderRecipient | None = None,
        template: Template | str | None = None,
        **kwargs,
    ) -> "ActionRequest":
        """
        Create a new ActionRequest instance.

        Args:
            function: The function to be invoked
            arguments: The arguments to be passed to the function
            sender: The sender of the request
            recipient: The recipient of the request

        Returns:
            ActionRequest: The new instance
        """
        content = prepare_action_request(function, arguments)
        content.update(kwargs)
        params = {
            "content": content,
            "sender": sender,
            "recipient": recipient,
            "role": MessageRole.ACTION,
        }
        if template:
            params["template"] = template
        return cls(**{k: v for k, v in params.items() if v is not None})

    def update(
        self,
        function: str = None,
        arguments: dict | None = None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        action_response: "ActionResponse" = None,  # type: ignore
        template: Template | str | None = None,
        **kwargs,
    ):
        if self.is_responded():
            raise ValueError("Cannot update a responded action request.")

        if (
            isinstance(action_response, RoledMessage)
            and action_response.class_name() == "ActionResponse"
        ):
            self.action_response_id = action_response.id

        if any([function, arguments]):
            action_request = prepare_action_request(
                function or self.function, arguments or self.arguments
            )
            self.content.update(action_request)
        super().update(
            sender=sender, recipient=recipient, template=template, **kwargs
        )

    def is_responded(self) -> bool:
        """
        Check if the action request has been responded to.

        Returns:
            bool: True if the request has a response, False otherwise
        """
        if self.action_response_id is not None:
            return True
        return False
