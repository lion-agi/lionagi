# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""AI assistant response handling for LionAGI's message system.

This module provides the AssistantResponse class, which represents responses
from AI models or assistants. It supports:

- Raw model output preservation
- Template-based response formatting
- Multiple response formats (streaming, single response)
- Structured data extraction from model outputs

The module includes utilities for preparing and formatting assistant responses,
with special handling for different model output formats (OpenAI, Anthropic, etc.).
"""
from typing import Any

from pydantic import BaseModel

from lionagi.utils import copy, is_same_dtype

from .base import MessageRole, SenderRecipient
from .message import MessageRole, RoledMessage, Template, jinja_env


def prepare_assistant_response(
    assistant_response: BaseModel | list[BaseModel] | dict | str | Any, /
) -> dict:
    """Prepare an AI model's response for storage and rendering.

    This function handles various response formats from different LLM providers:
    - OpenAI-style responses (choices[0].message.content)
    - Streaming responses (choices[0].delta.content)
    - Raw dictionaries with 'content' field
    - Plain strings or other formats

    Args:
        assistant_response: The raw response from an AI model, which could be:
            - A Pydantic model (e.g., OpenAI response)
            - A list of streaming chunks
            - A dictionary with model-specific structure
            - A plain string or other content

    Returns:
        dict: A standardized dictionary containing:
            - assistant_response: The extracted text content
            - model_response: The full model output (if available)

    Example:
        >>> response = prepare_assistant_response({
        ...     "choices": [{
        ...         "message": {"content": "Hello!"}
        ...     }]
        ... })
        >>> print(response)
        {'assistant_response': 'Hello!', 'model_response': {...}}
    """
    if assistant_response:
        content = {}
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
            content["assistant_response"] = str(assistant_response)
        return content
    else:
        return {"assistant_response": ""}


class AssistantResponse(RoledMessage):
    """A message representing an AI model's response.

    This class extends RoledMessage to handle responses from AI models,
    preserving both the human-readable content and the raw model output.
    It supports:
    - Multiple response formats (streaming, single response)
    - Template-based rendering
    - Raw model output preservation
    - Easy access to response content and metadata

    The class automatically extracts the relevant text from various model
    output formats (OpenAI, Anthropic, etc.) while preserving the complete
    model response in metadata for debugging or analysis.

    Properties:
        response (str): The extracted text portion of the response
        model_response (dict | list[dict]): The raw model output data
        template (Template | str | None): Template for rendering responses

    Example:
        >>> response = AssistantResponse.create(
        ...     assistant_response={
        ...         "choices": [{
        ...             "message": {"content": "Hello!"}
        ...         }]
        ...     }
        ... )
        >>> print(response.response)  # "Hello!"
        >>> print(response.model_response)  # Full model output
    """

    template: Template | str | None = jinja_env.get_template(
        "assistant_response.jinja2"
    )

    @property
    def response(self) -> str:
        """Get the text content of the assistant's response.

        This property provides easy access to the human-readable portion
        of the response, regardless of the original model output format.

        Returns:
            str: The extracted text content from the response.

        Example:
            >>> response.response
            "The capital of France is Paris."
        """
        return copy(self.content["assistant_response"])

    @response.setter
    def response(self, value: str) -> None:
        self.content["assistant_response"] = value

    @property
    def model_response(self) -> dict | list[dict]:
        """Access the raw model output data.

        This property provides access to the complete, unprocessed model
        response, which can be useful for:
        - Debugging model behavior
        - Accessing additional model metadata
        - Analyzing model confidence or other attributes
        - Handling provider-specific response fields

        Returns:
            dict | list[dict]: The complete model output, either as a
                single response dictionary or a list of streaming chunks.

        Example:
            >>> response.model_response
            {
                "id": "chatcmpl-123",
                "choices": [{
                    "message": {"content": "Hello!"},
                    "finish_reason": "stop"
                }]
            }
        """
        return copy(self.metadata.get("model_response", {}))

    @classmethod
    def create(
        cls,
        assistant_response: BaseModel | list[BaseModel] | dict | str | Any,
        sender: SenderRecipient | None = None,
        recipient: SenderRecipient | None = None,
        template: Template | str | None = None,
        **kwargs,
    ) -> "AssistantResponse":
        """
        Build an AssistantResponse from arbitrary assistant data.

        Args:
            assistant_response:
                A pydantic model, list, dict, or string representing
                an LLM or system response.
            sender (SenderRecipient | None):
                The ID or role denoting who sends this response.
            recipient (SenderRecipient | None):
                The ID or role to receive it.
            template (Template | str | None):
                Optional custom template.
            **kwargs:
                Additional content key-value pairs.

        Returns:
            AssistantResponse: The constructed instance.
        """
        content = prepare_assistant_response(assistant_response)
        model_response = content.pop("model_response", {})
        content.update(kwargs)
        params = {
            "content": content,
            "role": MessageRole.ASSISTANT,
            "recipient": recipient or MessageRole.USER,
        }
        if sender:
            params["sender"] = sender
        if template:
            params["template"] = template
        if model_response:
            params["metadata"] = {"model_response": model_response}
        return cls(**params)

    def update(
        self,
        assistant_response: (
            BaseModel | list[BaseModel] | dict | str | Any
        ) = None,
        sender: SenderRecipient | None = None,
        recipient: SenderRecipient | None = None,
        template: Template | str | None = None,
        **kwargs,
    ):
        """
        Update this AssistantResponse with new data or fields.

        Args:
            assistant_response:
                Additional or replaced assistant model output.
            sender (SenderRecipient | None):
                Updated sender.
            recipient (SenderRecipient | None):
                Updated recipient.
            template (Template | str | None):
                Optional new template.
            **kwargs:
                Additional content updates for `self.content`.
        """
        if assistant_response:
            content = prepare_assistant_response(assistant_response)
            self.content.update(content)
        super().update(
            sender=sender, recipient=recipient, template=template, **kwargs
        )


# File: lionagi/protocols/messages/assistant_response.py
