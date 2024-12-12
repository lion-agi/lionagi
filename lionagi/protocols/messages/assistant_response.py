# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import ClassVar

from pydantic import BaseModel, JsonValue
from typing_extensions import override

from lionagi.utils import copy

from ..base import ID
from .message import MessageFlag, MessageRole, RoledMessage, Template, env
from .utils import prepare_assistant_response


class AssistantResponse(RoledMessage):
    """
    Represents a response from an assistant in the system.

    This class handles responses from AI assistants, supporting both direct
    text responses and structured model outputs. It provides access to both
    the formatted response content and the underlying model data.

    Example:
        >>> response = AssistantResponse(
        ...     assistant_response="The answer is 42",
        ...     sender="assistant",
        ...     recipient="user"
        ... )
        >>> print(response.response)
        'The answer is 42'
    """

    template: ClassVar[Template] = env.get_template(
        "assistant_response.jinja2"
    )

    @override
    def __init__(
        self,
        assistant_response: BaseModel | JsonValue | MessageFlag,
        sender: ID.Ref | MessageFlag,
        recipient: ID.Ref | MessageFlag,
        protected_init_params: dict | None = None,
    ) -> None:
        """
        Initialize an AssistantResponse instance.

        Args:
            assistant_response: The content of the assistant's response
            sender: The sender of the response
            recipient: The recipient of the response
            protected_init_params: Protected initialization parameters
        """
        message_flags = [assistant_response, sender, recipient]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            protected_init_params = protected_init_params or {}
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",
            recipient=recipient,
        )

        content = prepare_assistant_response(assistant_response)
        if "model_response" in content:
            self.metadata["model_response"] = content.pop("model_response")
        self.content = content

    @property
    def response(self) -> str:
        """
        Get the assistant response content.

        Returns:
            str: The formatted content of the assistant's response
        """
        return self.template.render(self.content)

    @property
    def model_response(self) -> dict | list[dict]:
        """
        Get the underlying model response data.

        Returns:
            Union[dict, List[dict]]: The complete model response data
        """
        return copy(self.metadata.get("model_response", {}))

    @override
    def _format_content(self) -> dict[str, str]:
        return {"role": self.role.value, "content": self.response}
