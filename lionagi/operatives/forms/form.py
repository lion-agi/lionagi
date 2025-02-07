# forms/form.py

from typing import Any

from pydantic import ConfigDict, Field, model_validator
from typing_extensions import Self

from .base import BaseForm
from .flow import FlowDefinition


class Form(BaseForm):
    """
    A domain form that can handle either a simple 'a,b->c' assignment
    or a multi-step flow if the assignment string has semicolons, etc.
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    flow_definition: FlowDefinition | None = None
    # Possibly some extra fields, e.g. "guidance" or "task"
    guidance: str | None = Field(default=None)
    task: str | None = Field(default=None)

    @model_validator(mode="before")
    def parse_assignment_into_flow(cls, values):
        """
        If 'assignment' has semicolons, parse into a FlowDefinition with pass-through steps.
        If it's single-step or no semicolons, remain in simple mode (FlowDefinition=None).
        """
        assignment_str = values.get("assignment")
        if assignment_str and ";" in assignment_str:
            flow = FlowDefinition(name="auto_flow")
            flow.parse_flow_string(assignment_str)
            values["flow_definition"] = flow
        return values

    @model_validator(mode="after")
    def compute_output_fields(self) -> Self:
        """
        If we have a flow_definition, set `output_fields` to whatever is produced in the flow.
        If it's just single-step assignment, parse out the -> outputs if no output_fields given.
        """
        if self.flow_definition:
            produced = self.flow_definition.get_produced_fields()
            if not self.output_fields:
                self.output_fields = list(produced)
        else:
            # single-step
            if self.assignment and "->" in self.assignment:
                ins_outs = self.assignment.split("->", 1)
                outs_str = ins_outs[1]
                outs = [x.strip() for x in outs_str.split(",") if x.strip()]
                if not self.output_fields:
                    self.output_fields = outs
        return self

    def fill_fields(self, **kwargs) -> None:
        """
        Simple helper: fill fields of this form by assignment.
        Usually you'd do MyForm(field=..., field2=...),
        but partial updates might use fill_fields().
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_instructions(self) -> dict[str, Any]:
        """
        Return a dictionary that an LLM might read as 'instruction context'.
        """
        return {
            "assignment": self.assignment,
            "flow": (
                self.flow_definition.model_dump()
                if self.flow_definition
                else None
            ),
            "guidance": self.guidance,
            "task": self.task,
            "required_outputs": self.output_fields,
        }
