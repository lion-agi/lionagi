# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import ClassVar

from pydantic import BaseModel, Field


class Plan(BaseModel):
    title: str = Field(default_factory=str)
    description: str = Field(default_factory=str)


class ReActAnalysis(BaseModel):
    """
    A structured reason action framework for IPU. Captures the ReAct chain-of-thought
    output each round.

    Rules:
    ------
    - Fill in `analysis` and `extension_needed` fields every round.
    - Fill in `plans` and `corrections` fields as needed.
    - Do not repeat yourself.
    - Achieve the goal to user's satisfaction
    - Use the least amount of extensions.
    - Set extension_needed to True if ovrall goal is not yet achieved.
    - Do not set extension_needed to False, if just providing an interim answer

    Hint:
    -----
    - Make good use of your context window and action request order
    - Plan ahead
    - Review often
    """

    # Standard ReAct strings for controlling expansions:
    FIRST_EXT_PROMPT: ClassVar[str] = (
        "If needed, you can perform multiple reason-action steps for better achieving "
        "overall goal. Strategize according to the task at hand. "
        "You have up to {extensions} extensions in current ReAct operation. Please continue."
    )
    CONTINUE_EXT_PROMPT: ClassVar[str] = (
        "You are provided with another round. You still have up to {extensions} extensions "
        "in current ReAct operation. Please continue."
    )
    ANSWER_PROMPT: ClassVar[str] = (
        "Given your reasoning and actions, please now provide the final answer "
        "to the user's request:\n\n{instruction}"
    )
    analysis: str = Field(
        default_factory=str,
        description=(
            "Free-form reasoning or chain-of-thought. Commonly used for divide_and_conquer"
            ", brainstorming, reflections, regurgitation, review_checkpoints ...etc."
        ),
    )
    extension_needed: bool = Field(
        False,
        description="Set True if more rounds are needed. If False, final answer is next.",
    )
    plans: list[Plan] = Field(
        default_factory=list,
        description=(
            "Short descriptor for an upcoming activities the LLM wish to conduct"
        ),
    )
    corrections: list[str] = Field(
        default_factory=list,
        description=("List of corrections or adjustments to make "),
    )


class Analysis(BaseModel):

    answer: str
