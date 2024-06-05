from abc import ABC, abstractmethod

import os
import asyncio
import numpy as np
from dotenv import load_dotenv
from lionagi.os.libs import to_list, ninsert
from lionagi.os.libs.sys_util import create_id, get_timestamp
from lionagi.os.collections.abc import Component, ModelLimitExceededError
from lionagi.files.operations.tokenize.token_calculator import calculate_num_token

from ..api.service import BaseService
from ..api.status_tracker import StatusTracker


class ChatCompletionMixin(ABC):
    async def call_chat_completion(self, messages, **kwargs):
        """
        Asynchronous method to call the chat completion service.

        Args:
            messages (list): List of messages for the chat completion.
            **kwargs: Additional parameters for the service call.

        Returns:
            dict: Response from the chat completion service.
        """

        num_tokens = calculate_num_token(
            {"messages": messages},
            "chat/completions",
            self.endpoint_schema.get("token_encoding_name", None),
        )

        if num_tokens > self.token_limit:
            raise ModelLimitExceededError(
                f"Number of tokens {num_tokens} exceeds the limit {self.token_limit}"
            )

        return await self.service.serve_chat(
            messages, required_tokens=num_tokens, **kwargs
        )
