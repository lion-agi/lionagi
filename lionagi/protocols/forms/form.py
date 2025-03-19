# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

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
        If the 'assignment' has semicolons, assume multiple steps, parse into FlowDefinition.
        If it's a single step or no semicolons, we remain in 'simple' mode.
        """
        assignment_str = values.get("assignment")
        if assignment_str and ";" in assignment_str:
            flow = FlowDefinition()
            flow.parse_flow_string(assignment_str)
            values["flow_definition"] = flow
        return values

    @model_validator(mode="after")
    def compute_output_fields(self) -> Self:
        """
        If in simple mode, we parse something like 'a,b->c' and set output_fields=[c].
        If in multi-step mode, we set output_fields to the final produced fields of the flow.
        """
        if self.flow_definition:
            # multi-step
            produced = self.flow_definition.get_produced_fields()
            if not self.output_fields:
                self.output_fields = list(produced)
        else:
            # single-step
            if self.assignment and "->" in self.assignment:
                # parse the single arrow
                ins_outs = self.assignment.split("->", 1)
                outs_str = ins_outs[1]
                outs = [x.strip() for x in outs_str.split(",") if x.strip()]
                if not self.output_fields:
                    self.output_fields = outs
        return self

    def fill_fields(self, **kwargs) -> None:
        """
        A small helper: fill fields in this form by direct assignment.
        Usually you'd do 'myform(field=val, field2=val2)', but sometimes you want partial updates.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_instructions(self) -> dict[str, Any]:
        """
        Return a small dictionary that an LLM can read as an 'instruction context'.
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


# File: lionagi/protocols/forms/form.py
