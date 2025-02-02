# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Defines the `ActionRequest` class, a specific `RoledMessage` for requesting
a function or action call within LionAGI. It is typically accompanied by
arguments and can later be answered by an `ActionResponse`.
"""

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
    """
    Build a structured dict describing the request details.

    Args:
        function (str | Callable):
            The name (or callable) representing the function to invoke.
        arguments (dict):
            The arguments necessary for the function call.

    Returns:
        dict[str, Any]: A standardized dictionary containing
        'action_request' -> {'function':..., 'arguments':...}

    Raises:
        ValueError: If `function` is neither a string nor callable, or
            if `arguments` cannot be turned into a dictionary.
    """
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
    """
    A message that requests an action or function to be executed.
    It inherits from `RoledMessage` and includes function name,
    arguments, and optional linking to a subsequent `ActionResponse`.
    """

    template: Template | str | None = jinja_env.get_template(
        "action_request.jinja2"
    )

    @property
    def action_response_id(self) -> IDType | None:
        """
        Get or set the ID of the corresponding action response.

        Returns:
            IDType | None: The ID of the action response, or None if none assigned.
        """
        return self.content.get("action_response_id", None)

    @action_response_id.setter
    def action_response_id(self, action_response_id: IDType) -> None:
        self.content["action_response_id"] = str(action_response_id)

    @property
    def request(self) -> dict[str, Any]:
        """
        Get the entire 'action_request' dictionary if present.

        Returns:
            dict[str, Any]: The request content or empty dict if missing.
        """
        return copy(self.content.get("action_request", {}))

    @property
    def arguments(self) -> dict[str, Any]:
        """
        Access just the 'arguments' from the action request.

        Returns:
            dict[str, Any]: The arguments to be used by the function call.
        """
        return self.request.get("arguments", {})

    @property
    def function(self) -> str:
        """
        Name of the function to be invoked.

        Returns:
            str: The function name or empty string if none provided.
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
        Build a new ActionRequest.

        Args:
            function (str | Callable | None):
                The function or callable name.
            arguments (dict | None):
                Arguments for that function call.
            sender (SenderRecipient | None):
                The sender identifier or role.
            recipient (SenderRecipient | None):
                The recipient identifier or role.
            template (Template | str | None):
                Optional custom template.
            **kwargs:
                Extra key-value pairs to merge into the content.

        Returns:
            ActionRequest: A newly constructed instance.
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
        """
        Update this request with new function, arguments, or link to an
        action response.

        Args:
            function (str): New function name, if changing.
            arguments (dict): New arguments dictionary, if changing.
            sender (SenderRecipient): New sender.
            recipient (SenderRecipient): New recipient.
            action_response (ActionResponse):
                If provided, this request is flagged as responded.
            template (Template | str | None):
                Optional new template.
            **kwargs:
                Additional fields to store in content.

        Raises:
            ValueError: If the request is already responded to.
        """
        if self.is_responded():
            raise ValueError("Cannot update a responded action request.")

        # Link action response if given
        if (
            isinstance(action_response, RoledMessage)
            and action_response.class_name() == "ActionResponse"
        ):
            self.action_response_id = action_response.id

        # If new function or arguments, create new 'action_request' content
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
        Check if there's a linked action response.

        Returns:
            bool: True if an action response ID is present.
        """
        return self.action_response_id is not None


# File: lionagi/protocols/messages/action_request.py
