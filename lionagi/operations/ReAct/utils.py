# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import ClassVar, Literal

from pydantic import BaseModel, Field


class PlannedAction(BaseModel):
    """
    Short descriptor for an upcoming action/tool invocation the LLM wants to perform.
    The model can hold multiple actions in a single round if needed.
    """

    action_type: str = Field(
        ...,
        description="The name or type of tool/action to invoke (e.g., 'search_exa', 'reader_tool').",
    )
    description: str = Field(
        ...,
        description="A short explanation of why or what is intended to achieve with this action.",
    )


class ReActAnalysis(BaseModel):
    """
    Captures the ReAct chain-of-thought output each round:
    1) The LLM's 'analysis' (reasoning),
    2) A list of planned actions to perform before finalizing,
    3) Indication whether more expansions/rounds are needed,
    4) Additional tuning knobs: how to handle validation, how to execute actions, etc.
    Remember do not repeat yourself, and aim to use the most efficient way to achieve
    the goal to user's satisfaction.
    """

    # Standard ReAct strings for controlling expansions:
    FIRST_EXT_PROMPT: ClassVar[str] = (
        "You can perform multiple reason-action steps for accuracy. "
        "If you are not ready to finalize, set extension_needed to True. "
        "hint: you should set extension_needed to True if the overall goal"
        "is not yet achieved. Do not set it to False, if you are just providing"
        "an interim answer. You have up to {extensions} expansions. Please "
        "strategize accordingly and continue."
    )
    CONTINUE_EXT_PROMPT: ClassVar[str] = (
        "Another round is available. You may do multiple actions if needed. "
        "You have up to {extensions} expansions. Please strategize accordingly and continue."
    )
    ANSWER_PROMPT: ClassVar[str] = (
        "Given your reasoning and actions, please now provide the final answer "
        "to the user's request:\n\n{instruction}"
    )

    analysis: str = Field(
        ...,
        description=(
            "Free-form reasoning or chain-of-thought summary. Must be consistent with"
            " the plan. Commonly used for divide_and_conquer, brainstorming, reflections, "
            "regurgitation, review_checkpoints ...etc."
        ),
    )

    planned_actions: list[PlannedAction] = Field(
        default_factory=list,
        description=(
            "One or more short descriptors of the tool calls or operations "
            "the LLM wants to perform this round. For example, read the doc, "
            "then run a search."
        ),
    )

    extension_needed: bool = Field(
        False,
        description="Set True if more expansions are needed. If False, final answer is next.",
    )

    milestone: str | None = Field(
        None,
        description=(
            "A sub-goal or mini-checkpoint to reach before finalizing. "
            "E.g. 'Validate results from search_exa, then summarize outcomes.'"
        ),
    )

    action_strategy: Literal["sequential", "concurrent", "batch"] = Field(
        "concurrent",
        description=(
            "Specifies how to invoke the planned actions:\n"
            "'sequential' => Each action is run in order, \n"
            "'concurrent' => All actions run in parallel, \n"
            "'batch' => Divide actions into async batches of N (if reasonable)."
        ),
    )

    action_batch_size: int | None = Field(
        None,
        description=(
            "provide if and only if action_strategy is 'batch', this specifies the number of actions to run in parallel per batch."
        ),
    )


class Analysis(BaseModel):

    answer: str
