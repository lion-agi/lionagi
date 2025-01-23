# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import ClassVar, Literal

from pydantic import BaseModel, Field, field_validator

from lionagi.libs.validate.common_field_validators import (
    validate_boolean_field,
)
from lionagi.libs.validate.fuzzy_validate_mapping import fuzzy_validate_mapping
from lionagi.utils import to_num


class PlannedAction(BaseModel):
    """
    Short descriptor for an upcoming action/tool invocation the LLM wants to perform.
    The model can hold multiple actions in a single round if needed.
    """

    action_type: str | None = Field(
        default_factory=str,
        description=(
            "The name or type of tool/action to invoke (e.g., 'search_exa',"
            " 'reader_tool') tool must exist in tool schemas."
        ),
    )
    description: str | None = Field(
        default_factory=str,
        description="A short explanation of why or what is intended to achieve with this action.",
    )

    @field_validator("action_type", "description", mode="before")
    def _validate_action_type(cls, values):
        if values is None:
            return None
        return str(values)


class ReActAnalysis(BaseModel):
    """
    Captures the ReAct chain-of-thought output each round:
    1) The LLM's 'analysis' (reasoning),
    2) A list of planned actions to perform before finalizing,
    3) Indication whether more expansions/rounds are needed,
    4) Additional tuning knobs: how to handle validation, how to execute actions, etc.
    """

    # Standard ReAct strings for controlling expansions:
    FIRST_EXT_PROMPT: ClassVar[str] = (
        "You can perform multiple reason-action steps for accuracy. "
        "If you are not ready to finalize, set extension_needed to True. "
        "You have up to {extensions} expansions. Please continue."
    )
    CONTINUE_EXT_PROMPT: ClassVar[str] = (
        "Another round is available. You may do multiple actions if needed. "
        "You have up to {extensions} expansions. Please continue."
    )
    ANSWER_PROMPT: ClassVar[str] = (
        "Given your reasoning and actions, please now provide the final answer "
        "to the user's request:\n\n{instruction}"
    )

    analysis: str | None = Field(
        None,
        description="Free-form reflective reasoning/chain-of-thought. Must be consistent with the plan.",
    )

    planned_actions: list[PlannedAction] | None = Field(
        default_factory=list,
        description=(
            "One or more short descriptors of the tool calls or operations "
            "the LLM wants to perform this round. For example, read the doc, "
            "then run a search."
        ),
    )

    extension_needed: bool | None = Field(
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
            "typically only run in sequence if actions depend on each other (side effects)."
            "if the actions are independent, run in parallel or batch for speed."
        ),
    )

    action_batch_size: int | None = Field(
        None,
        description=(
            "provide if and only if action_strategy is 'batch', this specifies "
            "the number of actions to run in parallel per batch."
        ),
    )

    @field_validator("extension_needed", mode="before")
    def _validate_extension_needed(cls, values):
        return validate_boolean_field(cls, values, False)

    @field_validator("action_batch_size", mode="before")
    def _validate_action_batch_size(cls, values):
        if values is None:
            return None
        try:
            return to_num(values, num_type=int)
        except ValueError:
            return None

    @field_validator("action_strategy", mode="before")
    def _validate_action_strategy(cls, values):
        if values not in ["sequential", "concurrent", "batch"]:
            return "concurrent"
        return values

    @field_validator("planned_actions", mode="before")
    def _validate_planned_actions(cls, values):
        if not values:
            return None
        values = [] if not isinstance(values, list) else values

        out = []
        for i in values:
            j = fuzzy_validate_mapping(
                i,
                ["action_type", "description"],
                suppress_conversion_errors=True,
            )
            if j:
                out.append(
                    PlannedAction(
                        action_type=j["action_type"],
                        description=j["description"],
                    )
                )
        return out
