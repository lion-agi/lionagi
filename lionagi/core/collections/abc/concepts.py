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

"""This module defines abstract base classes for LionAGI."""

from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any, Iterator, TypeVar

from pydantic import Field, BaseModel, field_validator

from .exceptions import LionTypeError

T = TypeVar("T")


class Progressable(ABC):
    """Represents a process that can progress forward asynchronously."""

    @abstractmethod
    async def forward(self, /, *args: Any, **kwargs: Any) -> None:
        """Move the process forward asynchronously.

        Args:
            *args: Positional arguments for moving the process forward.
            **kwargs: Keyword arguments for moving the process forward.
        """


class Executable(ABC):
    """Represents an object that can be executed with arguments."""

    @abstractmethod
    async def execute(self, /, *args: Any, **kwargs: Any) -> Any:
        """Execute the object with the given arguments asynchronously.

        Args:
            *args: Positional arguments for executing the object.
            **kwargs: Keyword arguments for executing the object.

        Returns:
            Any: The result of executing the object.
        """


class Directive(ABC):
    """Represents a directive that can be directed with arguments."""

    # @abstractmethod
    # async def direct(self, *args, **kwargs):
    #     """Direct the directive with the given arguments asynchronously.

    #     Args:
    #         *args: Positional arguments for directing the directive.
    #         **kwargs: Keyword arguments for directing the directive.
    #     """

    @property
    def class_name(self) -> str:
        """Get the class name of the directive.

        Returns:
            str: The class name of the directive.
        """
        return self._class_name()

    @classmethod
    def _class_name(cls) -> str:
        """Get the class name of the directive.

        Returns:
            str: The class name of the directive.
        """
        return cls.__name__
