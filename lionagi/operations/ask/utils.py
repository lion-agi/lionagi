# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING, Any, ClassVar, Union

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from lionagi.session.branch import Branch
    from lionagi.service.imodel import iModel

from lionagi.service.imodel import iModel


class AskAnalysis(BaseModel):
    """Model for ask operation analysis"""

    # Standard prompts for different targets
    BRANCH_PROMPT: ClassVar[
        str
    ] = """Query for branch {target}:
{query}"""

    MODEL_PROMPT: ClassVar[
        str
    ] = """Query for model:
{query}"""

    EXTERNAL_PROMPT: ClassVar[
        str
    ] = """Query for external system {target}:
{query}"""

    response: Any = Field(..., description="The response from the target")

    @classmethod
    def format_prompt(
        cls, query: str, target: Union["Branch", iModel, str]
    ) -> str:
        """Format appropriate prompt based on target type"""
        if isinstance(target, iModel):
            return cls.MODEL_PROMPT.format(query=query)

        target_id = getattr(target, "id", str(target))
        if isinstance(target, type(BaseModel)):  # Branch type check
            return cls.BRANCH_PROMPT.format(target=target_id, query=query)

        return cls.EXTERNAL_PROMPT.format(target=target_id, query=query)
