from typing import Any, Callable, Optional, List
from lionagi.core.generic.base.base_component import BaseComponent
from ..lionagi.libs.ln_validate import validation_funcs


class PromptField(BaseComponent):
    default: Any = None
    description: str = ""
    required: bool = False
    choices: Optional[List[Any]] = None
    validator: Optional[Callable] = None
    field_type: str = "str"
    fix_: bool = False

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.default is not None:
            self.default = self.validate_and_fix(self.default, fix_=self.fix_)

    @property
    def value(self):
        return self.default

    @value.setter
    def value(self, new_value):
        self.default = self.validate_and_fix(new_value)

    def validate_and_fix(self, value, fix_=False, **kwargs):

        if self.validator:
            return self.validator(value, **kwargs)

        if self.field_type == "enum" or self.choices is not None:
            return validation_funcs["enum"](
                value, choices=self.choices, fix_=fix_, **kwargs
            )

        elif self.field_type in ["bool", "boolean"]:
            return validation_funcs["bool"](value, fix_=fix_, **kwargs)

        elif self.field_type in ["int", "float", "number", "num"]:
            return validation_funcs["number"](value, fix_=fix_, **kwargs)

        elif self.field_type in ["str", "string", "text"]:
            return validation_funcs["str"](value, fix_=fix_, **kwargs)

        else:
            raise TypeError(f"Invalid field type {self.field_type}")

    def __repr__(self) -> str:
        return f"PromptField(default={self.default}, description={self.description}, required={self.required}, choices={self.choices}, field_type={self.field_type})"
