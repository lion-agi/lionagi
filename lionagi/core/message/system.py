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
from ..collections.abc import Field
from .message import RoledMessage, MessageRole


class System(RoledMessage):

    system: str | Any | None = Field(None)

    def __init__(self, system=None, sender=None, recipient=None, **kwargs):
        if not system:
            if "metadata" in kwargs and "system" in kwargs["metadata"]:
                system = kwargs["metadata"].pop("system")

        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content={"system_info": system},
            recipient=recipient or "N/A",
            system=system,
            **kwargs,
        )

    @property
    def system_info(self):
        """
        Retrieves the system information stored in the message content.
        """
        return self.content["system_info"]
