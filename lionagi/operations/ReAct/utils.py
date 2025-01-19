# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import ClassVar

from pydantic import BaseModel, Field


class ReActAnalysis(BaseModel):

    FIRST_EXT_PROMPT: ClassVar[str] = (
        "You are provided with additional rounds to perform reason action to provide an accurate final answer. you have max another {extensions} rounds. Pleasen continue."
    )

    CONTINUE_EXT_PROMPT: ClassVar[str] = (
        "You are provided with another round, you have max another {extensions} rounds. Please continue."
    )

    ANSWER_PROMPT: ClassVar[str] = (
        "given above reason and actions, please provide final answer to the original user request:\n\n {instruction}"
    )

    analysis: str
    extension_needed: bool = Field(
        False,
        description="Set to True if more steps are needed to provide an accurate answer. If True, additional rounds are allowed. Typically should be set to true if more actions should be taken or planned to be taken. If false, will proceed to provide final answer next.",
    )
