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
    Represents an operation to process a single FlowStep, referencing:
      - FlowStep (inputs -> outputs)
      - A Form that stores the actual data
      - Optional transform technique / branch if you want LLM transformations
    """

    step: FlowStep = Field(..., description="Flow step definition")
    form: Form = Field(
        ..., description="The Form instance storing input+output fields"
    )

    # Optionally store a reference to the branch if you do GPT-based transforms
    branch: "Branch" | None = Field(None, exclude=True)

    # If the step triggers a transform or function call, specify "technique"
    transform_technique: str | None = Field(
        default=None,
        description="Optional transform technique, e.g. 'someLang'",
    )
    transform_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra parameters for the transformation step, if used",
    )

    async def invoke(self) -> None:
        """
        Processes this single step by reading inputs from the Form,
        applying transformations, and storing outputs in the Form.
        """
        self.status = EventStatus.PROCESSING
        try:
            # 1) Gather inputs
            inputs = {i: getattr(self.form, i, None) for i in self.step.inputs}

            # 2) If there's a transform technique & branch, do a "branch.transform"
            #    or local approach. This is an example usage:
            if self.transform_technique and self.branch:
                combined_input = "\n".join(
                    str(v) for v in inputs.values() if v
                )
                transformed = await self.branch.transform(
                    data=combined_input,
                    technique=self.transform_technique,
                    technique_kwargs=self.transform_kwargs,
                )
                # store in the first output, or you might do something else
                if self.step.outputs:
                    setattr(self.form, self.step.outputs[0], transformed)
            else:
                # 2b) If no transform_technique, we can just re-use the step logic:
                self.step.run(self.form)

            # Done
            self.form.has_processed = True
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
        If needed, implement partial step streaming. For now, same as invoke().
        """
        await self.invoke()

    @property
    def request(self) -> dict:
        """
        Optionally return data that might be used for concurrency checks or rate-limits.
        """
        return {"some_step_name": self.step.name}

    def to_log(self) -> Log:
        """Return a structured log entry."""
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
