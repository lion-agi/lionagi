# forms/flow_event.py

import asyncio
from typing import TYPE_CHECKING, Any

from pydantic import Field

from lionagi.protocols.generic.event import Event, EventStatus
from lionagi.protocols.generic.log import Log
from lionagi.utils import to_dict

from .flow import FlowStep
from .form import Form

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


class FlowStepEvent(Event):
    """
    Represents an operation to process a single FlowStep within a multi-step flow,
    using (or updating) a Form that stores inputs/outputs.

    On `.invoke()`, we attempt to read the step inputs from the form,
    transform them (if needed), and write the outputs back into the form.

    If the step requires an LLM-based transformation or external logic,
    we can optionally do that as well.
    """

    # The flow step definition: which inputs->outputs, etc.
    step: FlowStep = Field(..., description="Flow step definition")

    # The form we are operating on.
    form: Form = Field(
        ..., description="The Form instance storing input+output fields"
    )

    # Possibly store a reference to the branch, or get it injected at runtime
    branch: "Branch" | None = Field(None, exclude=True)

    # If the step triggers a transform or function call, specify "technique"
    transform_technique: str | None = Field(
        default=None,
        description="Optional transform technique, e.g. 'synthlang'",
    )
    transform_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for the transformation step if needed",
    )

    async def invoke(self) -> None:
        """
        Processes this flow step by reading inputs, applying transformations, and
        writing outputs to the form. The logic may vary by step definition or transform technique.
        """
        self.status = EventStatus.PROCESSING
        try:
            # 1) Gather step inputs from the form
            inputs = {}
            for i in self.step.inputs:
                val = getattr(self.form, i, None)
                inputs[i] = val

            # 2) If there's a transform technique, call branch.transform(...) or local code
            if self.transform_technique and self.branch:
                # Let's assume we only transform the first input or a combined input
                # In a real system, you'd define how to handle multi-input transforms
                combined_input = "\n".join(
                    str(v) for v in inputs.values() if v
                )
                transformed = await self.branch.transform(
                    data=combined_input,
                    technique=self.transform_technique,
                    technique_kwargs=self.transform_kwargs,
                    # you can choose store_result_as_message, etc.
                )
                # We'll store the result in an output field (like the first in self.step.outputs?)
                if self.step.outputs:
                    out_field = self.step.outputs[0]
                    setattr(self.form, out_field, transformed)
            else:
                # 2b) If no transform_technique is given, we might do a local pass-through
                # or do some domain logic
                for out_field in self.step.outputs:
                    # trivial pass-through, just copy from first input
                    if self.step.inputs:
                        val = inputs[self.step.inputs[0]]
                        setattr(self.form, out_field, val)

            # 3) Mark the form's has_processed = True if this step completes its portion
            # Or we might do more elaborate logic: only if last step?
            self.form.has_processed = True

            # 4) Done
            self.execution.response = {
                "step": self.step.name,
                "form_updates": {
                    o: getattr(self.form, o, None) for o in self.step.outputs
                },
            }
            self.status = EventStatus.COMPLETED

        except Exception as e:
            self.execution.error = str(e)
            self.status = EventStatus.FAILED

    async def stream(self) -> None:
        """
        If we needed streaming logic, we could implement it here.
        For now, we just call invoke.
        """
        await self.invoke()

    @property
    def request(self) -> dict:
        """
        Optionally return a dictionary that might be used for rate-limiting or concurrency checks.
        """
        return {"required_tokens": None, "some_step_name": self.step.name}

    def to_log(self) -> Log:
        """Create a Log object summarizing this event."""
        return Log(
            content={
                "type": "FlowStepEvent",
                "step": self.step.name,
                "form_id": self.form.id,
                "transform_technique": self.transform_technique,
                "kwargs": self.transform_kwargs,
                "status": str(self.status),
                "response": to_dict(self.execution.response),
                "error": self.execution.error,
            }
        )
