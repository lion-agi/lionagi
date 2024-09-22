from enum import Enum
from typing import Any
from pydantic import Field
from lionagi.core.report.form import Form
from lionagi.core.manual.guide import OperationGuide

from lion_core.libs import to_dict


class TaskStatus(str, Enum):
    """Enumeration of task result statuses."""

    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    WAITING = "waiting"
    HELP_NEEDED = "help_needed"


class ExpertForm(Form):
    """Base class for expert forms used in the AutoOS system."""

    operation_name: str | None = None

    thinking_style: Any = Field(
        default=None,
        description=(
            "A style, technique, or perspective of thinking that can be used to "
            "solve the task at hand better."
        ),
    )
    guidance: Any = Field(
        default=None,
        description="General guidance or principles for the task.",
    )
    instruction: Any = Field(
        None,
        description="Specific instructions for the task.",
    )
    context: Any = Field(
        None,
        description="Context of the task at hand.",
    )
    task_status: TaskStatus | str | None = Field(
        default=None,
        description=(
            "Indicates the status of task of interest. Pick one of the following:\n"
            "1. completed: Process satisfied all the requirements and planned goals successfully.\n"
            "2. in_progress: Task is still being worked on.\n"
            "3. failed: Task ended, failing to meet the requirements or goals.\n"
            "4. waiting: Task is on halt, waiting for further instructions or resources.\n"
            "5. help_needed: Task requires assistance from human or supervior agents to accurately deliver the expected outcome.\n"
        ),
    )
    reflection: str | None = Field(
        None,
        description=(
            "Reflection on the task, including critical thinking, analysis of the problem "
            "from different perspectives, questioning assumptions, and evaluating evidence. "
            "Explain your trace of thought and why you did what you did."
        ),
    )
    plans: str | dict[str, Any] | None = Field(
        None,
        description=(
            "Apply divide and conquer strategies. Plans should be presented in steps, "
            "with each step including: step number, goal, reason, action, expected outcome, "
            "what-ifs, and refined action."
        ),
        examples=[
            {
                "step_1": {
                    "step_goal": "Understand the requirements",
                    "reason": "To ensure all constraints are met.",
                    "action": "Read the task description carefully.",
                    "expected_outcome": "Clear understanding of the task.",
                    "what_ifs": "If unclear, ask for clarification.",
                    "refined_action": "Proceed to implementation.",
                },
                "step_2": "...",
            }
        ],
    )
    chatted: bool | None = Field(
        False,
        description="Indicates if the form has been processed by an AI.",
    )
    extension_forms: list = []

    def __init__(
        self,
        operation: OperationGuide | None = None,
        operation_name=None,
        operation_assignment=None,
        operation_thinking_style=None,
        operation_instruction=None,
        operation_guidance=None,
        operation_context=None,
        **kwargs,
    ):
        _config = {
            "operation_name": operation_name,
            "operation_assignment": operation_assignment,
            "operation_thinking_style": operation_thinking_style,
            "operation_instruction": operation_instruction,
            "operation_guidance": operation_guidance,
            "operation_context": operation_context,
        }
        _config2 = to_dict(operation, use_model_dump=True)

        _config = {k: v for k, v in _config.items() if v is not None}
        _config2 = {k: v for k, v in _config2.items() if v is not None}
        _config = {**_config, **_config2, **kwargs}

        super().__init__(
            operation_name=_config.pop("operation_name", None),
            thinking_style=_config.pop("operation_thinking_style", None),
            guidance=_config.pop("operation_guidance", None),
            instruction=_config.pop("operation_instruction", None),
            context=_config.pop("operation_context", None),
            assignment=_config.pop("operation_assignment", None),
            **_config,
        )
        if isinstance(operation, OperationGuide):
            self.metadata["operation"] = {
                "operation_name": operation.operation_name,
                "operation_version": operation.operation_version,
            }
        if self.thinking_style is not None:
            self.append_to_input("thinking_style")
        if self.context is not None:
            self.append_to_input("context")
        if self.guidance is not None:
            self.append_to_input("guidance")
        if "task_status" not in self.work_fields:
            self.append_to_request("task_status")
