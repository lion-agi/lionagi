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
from pydantic import Field
from lionagi.os.lib.sys_util import get_now
from .message import RoledMessage, MessageRole


class System(RoledMessage):
    """
    Represents a system message with system-related information.

    Inherits from `RoledMessage` and provides methods to manage system-specific content.

    Attributes:
        system (str | Any | None): The system information.
    """

    system: str | Any | None = Field(None)

    def __init__(
        self,
        system=None,
        sender=None,
        recipient=None,
        system_datetime: bool | str = None,
        system_datetime_strftime: str = None,
        **kwargs,
    ):
        """
        Initializes the System message.

        Args:
            system (str or Any, optional): The system information.
            sender (str, optional): The sender of the message.
            recipient (str, optional): The recipient of the message.
            system_datetime (bool | str, optional): The system datetime, if True, it will be set to the current datetime. if str, it will be set to the given datetime.
            system_datetime_strftime (str, optional): The system datetime strftime format.
            **kwargs: Additional fields to be added to the message content, must be JSON serializable.
        """
        if not system:
            if "metadata" in kwargs and "system" in kwargs["metadata"]:
                system = kwargs["metadata"].pop("system")

        if system_datetime is not None:
            if isinstance(system_datetime, bool) and system_datetime:
                system_datetime = get_now(datetime_=True)
                system_datetime = (
                    system_datetime.strftime("%Y-%m-%d %H:%M")
                    if not system_datetime_strftime
                    else system_datetime.strftime(system_datetime_strftime)
                )
            elif isinstance(system_datetime, str):
                pass

        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content=(
                {"system_info": f"{system}. System Date: {system_datetime}"}
                if system_datetime
                else {"system_info": system}
            ),
            recipient=recipient or "N/A",
            system=system,
            **kwargs,
        )

    @property
    def system_info(self):
        """
        Retrieves the system information stored in the message content.

        Returns:
            Any: The system information.
        """
        return self.content["system_info"]

    def clone(self, **kwargs):
        """
        Creates a copy of the current System object with optional additional arguments.

        This method clones the current object, preserving its content.
        It also retains the original metadata, while allowing
        for the addition of new attributes through keyword arguments.

        Args:
            **kwargs: Optional keyword arguments to be included in the cloned object.

        Returns:
            System: A new instance of the object with the same content and additional keyword arguments.
        """
        import json

        system = json.dumps(self.system_info)
        system_copy = System(system=json.loads(system), **kwargs)
        system_copy.metadata["origin_ln_id"] = self.ln_id
        return system_copy
