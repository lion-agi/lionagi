"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any
from .message import RoledMessage, MessageRole


class AssistantResponse(RoledMessage):

    def __init__(
        self,
        assistant_response: Any = None,
        sender: str | None = None,
        recipient: str | None = None,
        **kwargs,
    ):

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",
            content={"assistant_response": assistant_response["content"]},
            recipient=recipient,
            **kwargs,
        )

    def clone(self, **kwargs):
        import json

        content = json.dumps(self.content["assistant_response"])
        content = {"content": json.loads(content)}
        response_copy = AssistantResponse(assistant_response=content, **kwargs)
        response_copy.metadata["origin_ln_id"] = self.ln_id
        return response_copy
