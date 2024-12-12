# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from pydantic import BaseModel, Field

MessageContentType = Union[str, list[Union[dict, str]], None]


__all__ = (
    "CodeBlock",
    "CodeResult",
    "CodeExtractor",
    "CodeExecutor",
    "CodeExecutionConfig",
    "CommandLineCodeResult",
    "IPythonCodeResult",
    "UserMessageTextContentPart",
    "UserMessageImageContentPart",
)


class UserMessageTextContentPart(TypedDict):
    type: Literal["text"]
    text: str


class UserMessageImageContentPart(TypedDict):
    type: Literal["image_url"]
    # Ignoring the other "detail param for now"
    image_url: dict[Literal["url"], str]


class CodeBlock(BaseModel):
    """(Experimental) A class that represents a code block."""

    code: str = Field(description="The code to execute.")

    language: str = Field(description="The language of the code.")


class CodeResult(BaseModel):
    """(Experimental) A class that represents the result of a code execution."""

    exit_code: int = Field(description="The exit code of the code execution.")

    output: str = Field(description="The output of the code execution.")


class CodeExtractor(Protocol):
    """(Experimental) A code extractor class that extracts code blocks from a message."""

    def extract_code_blocks(
        self,
        message: (
            str
            | list[UserMessageTextContentPart | UserMessageImageContentPart]
            | None
        ),
    ) -> list[CodeBlock]:
        """(Experimental) Extract code blocks from a message.

        Args:
            message (str): The message to extract code blocks from.

        Returns:
            List[CodeBlock]: The extracted code blocks.
        """
        ...  # pragma: no cover


@runtime_checkable
class CodeExecutor(Protocol):
    """(Experimental) A code executor class that executes code blocks and returns the result."""

    @property
    def code_extractor(self) -> CodeExtractor:
        """(Experimental) The code extractor used by this code executor."""
        ...  # pragma: no cover

    def execute_code_blocks(self, code_blocks: list[CodeBlock]) -> CodeResult:
        """(Experimental) Execute code blocks and return the result.

        This method should be implemented by the code executor.

        Args:
            code_blocks (List[CodeBlock]): The code blocks to execute.

        Returns:
            CodeResult: The result of the code execution.
        """
        ...  # pragma: no cover

    def restart(self) -> None:
        """(Experimental) Restart the code executor.

        This method should be implemented by the code executor.

        This method is called when the agent is reset.
        """
        ...  # pragma: no cover


class IPythonCodeResult(CodeResult):
    """(Experimental) A code result class for IPython code executor."""

    output_files: list[str] = Field(
        default_factory=list,
        description="The list of files that the executed code blocks generated.",
    )


CodeExecutionConfig = TypedDict(
    "CodeExecutionConfig",
    {
        "executor": Union[
            Literal["ipython-embedded", "commandline-local"], CodeExecutor
        ],
        "last_n_messages": Union[int, Literal["auto"]],
        "timeout": int,
        "use_docker": Union[bool, str, list[str]],
        "work_dir": str,
        "ipython-embedded": Mapping[str, Any],
        "commandline-local": Mapping[str, Any],
    },
    total=False,
)


class CommandLineCodeResult(CodeResult):
    """(Experimental) A code result class for command line code executor."""

    code_file: str | None = Field(
        default=None,
        description="The file that the executed code block was saved to.",
    )