# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import ClassVar

from pydantic import BaseModel, Field


class ReActAnalysis(BaseModel):

    FIRST_EXT_PROMPT: ClassVar[str] = (
        "You are provided with another round to perform reason action to provide an accurate final answer. you have max another {extensions} rounds, set extension_needed to False if you are done and ready to provide final answer."
    )

    CONTINUE_EXT_PROMPT: ClassVar[str] = (
        "You are provided with another round, you have max another {extensions} rounds"
    )

    ANSWER_PROMPT: ClassVar[str] = (
        "given above reason and actions, please provide final answer to the original user request {instruction}"
    )

    analysis: str
    extension_needed: bool = Field(
        False,
        description="Set to True if more steps are needed to provide an accurate answer. If True, additional rounds are allowed.",
    )
