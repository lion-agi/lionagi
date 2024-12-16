# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.core.typing import ID, Any, BaseModel, JsonValue, Note, override
from lionagi.libs.parse import to_str
from lionagi.libs.utils import copy, is_same_dtype

from .message import MessageFlag, MessageRole, RoledMessage


def prepare_assistant_response(
    assistant_response: BaseModel | list[BaseModel] | dict | str | Any, /
) -> Note:
    """
    Prepare an assistant's response for storage and transmission.

    This function handles various input formats including:
    - Single model outputs (response.choices[0].message.content)
    - Streaming responses (response[i].choices[0].delta.content)
    - Direct content in dictionaries or strings

    Args:
        assistant_response: The response content in any supported format

    Returns:
        Note: Formatted response content
    """
    if assistant_response:
        content = Note()
        # Handle model.choices[0].message.content format
        if isinstance(assistant_response, BaseModel):
            content["assistant_response"] = (
                assistant_response.choices[0].message.content or ""
            )
            content["model_response"] = assistant_response.model_dump(
                exclude_none=True, exclude_unset=True
            )
        # Handle streaming response[i].choices[0].delta.content format
        elif isinstance(assistant_response, list):
            if is_same_dtype(assistant_response, BaseModel):
                msg = "".join(
                    [
                        i.choices[0].delta.content or ""
                        for i in assistant_response
                    ]
                )
                content["assistant_response"] = msg
                content["model_response"] = [
                    i.model_dump(
                        exclude_none=True,
                        exclude_unset=True,
                    )
                    for i in assistant_response
                ]
            elif is_same_dtype(assistant_response, dict):
                msg = "".join(
                    [
                        i["choices"][0]["delta"]["content"] or ""
                        for i in assistant_response
                    ]
                )
                content["assistant_response"] = msg
                content["model_response"] = assistant_response
        elif isinstance(assistant_response, dict):
            if "content" in assistant_response:
                content["assistant_response"] = assistant_response["content"]
            elif "choices" in assistant_response:
                content["assistant_response"] = assistant_response["choices"][
                    0
                ]["message"]["content"]
            content["model_response"] = assistant_response
        elif isinstance(assistant_response, str):
            content["assistant_response"] = assistant_response
        else:
            content["assistant_response"] = to_str(assistant_response)
        return content
    else:
        return Note(assistant_response="")


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
        return copy(self.content["assistant_response"])

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
