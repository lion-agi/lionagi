"""
This module defines classes for creating and managing prompt templates,
including base templates and scored templates with additional attributes
like confidence scores and reasons.
"""

from typing import Any
from pydantic import Field

from ..schema.base_component import BaseComponent
from .mixin import PromptTemplateMixin


class PromptTemplate(BaseComponent, PromptTemplateMixin):
    template_name: str = Field(
        default="default_prompt_template",
        description="The name of the prompt template.",
    )
    signature: str = Field("null", description="signature indicating inputs, outputs")
    version: str | float | int | None = Field(
        default=None, description="The version of the prompt template."
    )
    description: str | dict[str, Any] | None | Any = Field(
        default=None, description="The description of the prompt template."
    )
    task: str | dict[str, Any] | None = Field(
        default=None, description="The task associated with the prompt template."
    )
    out_validation_kwargs: dict[str, Any] = Field(
        default_factory=dict, description="validation kwargs for output"
    )
    in_validation_kwargs: dict[str, Any] = Field(
        default_factory=dict, description="validation kwargs for input"
    )
    fix_input: bool = Field(True, description="whether to fix input")
    fix_output: bool = Field(True, description="whether to fix output")
    input_fields: list[str] = Field(
        default_factory=list, description="Extracted input fields from the signature."
    )
    output_fields: list[str] = Field(
        default_factory=list, description="Extracted output fields from the signature."
    )
    choices: dict[str, list[str]] = Field(
        default_factory=dict, description="Choices available for each template field."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_fields, self.output_fields = self._get_input_output_fields(
            self.signature
        )
        self.process(in_=True)

    @property
    def prompt_fields(self):
        return self.input_fields + self.output_fields

    @property
    def instruction_context(self):
        a = "".join(
            f"""
        ## input: {i}:
        - description: {self.model_fields[i].description}
        - value: {str(self.__getattribute__(self.input_fields[idx]))}
        """
            for idx, i in enumerate(self.input_fields)
        )
        return a.replace("        ", "")

    @property
    def instruction(self):
        ccc = f"""
        0. Your task is {self.task},
        1. provided: {self.input_fields}, 
        2. requested: {self.output_fields}
        ----------
        """
        return ccc.replace("        ", "")

    @property
    def instruction_output_fields(self):
        return {i: self.model_fields[i].description for i in self.output_fields}

    @property
    def inputs(self):
        return {i: getattr(self, i) for i in self.input_fields}

    @property
    def outputs(self):
        return {i: getattr(self, i) for i in self.output_fields}

    def process(self, in_=None, out_=None):
        if in_:
            self._process_input(fix_=self.fix_input)
            self._validate_input_choices(fix_=self.fix_input)
        if out_:
            self._process_response(out_, fix_=self.fix_output)
            self._validate_output_choices(fix_=self.fix_output)
        return self
