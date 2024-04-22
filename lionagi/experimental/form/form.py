from typing import Any, Type
from pydantic import Field
from lionagi.core.generic import BaseComponent
from .util import get_input_output_fields, system_fields


class Form(BaseComponent):

    assignment: str = Field(
        ..., 
        examples=["input1, input2 -> output"]
    )

    input_fields: list[str] = Field(default_factory=list)
    output_fields: list[str] = Field(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_fields, self.output_fields = get_input_output_fields(
            self.assignment
        )

    def to_dict(self):
        keys = list(self.model_fields.keys())
        return {
            k: self.__getattribute__(k) for k in keys
        }

    @property
    def work_fields(self):
        dict_ = self.to_dict()
        return {
            k: v for k, v in dict_.items() 
            if k not in system_fields
        }

    @property
    def filled(self):
        return all([value is not None for _, value in self.work_fields.items()])

    def fill(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.model_fields:
                self.__setattr__(k, v)