from abc import ABC
from enum import Enum
from datetime import datetime, date, time
from typing import Any, Callable, Optional

from pydantic import field_validator

from lionagi.libs import convert
from lionagi.core.schema.base_node import BaseComponent


class FieldType(str, Enum):
    NUMERIC = "number"
    ENUM = "enum"
    STRING = "string"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    LIST = "list"
    DICT = "dict"


class InputOutput(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    BOTH = "both"


def validate_number_field(x):
    if not isinstance(x, (int, float)):
        raise ValueError(f"Default value for NUMERIC must be an int or float, got {type(x).__name__}")

def validate_bool_field(x):
    if not isinstance(x, bool):
        raise ValueError(f"Default value for BOOLEAN must be a bool, got {type(x).__name__}")

def validate_str_field(x):
    if not isinstance(x, str):
        raise ValueError(f"Default value for STRING must be a str, got {type(x).__name__}")

def validate_datetime_field(x):
    if not isinstance(x, (datetime, str, date, time)):
        raise ValueError(f"Default value for DATE must be a datetime or str, got {type(x).__name__}")
    
def validate_list_field(x):
    if not isinstance(x, list):
        raise ValueError(f"Default value for LIST must be a list, got {type(x).__name__}")

def validate_dict_field(x):
    if not isinstance(x, dict):
        raise ValueError(f"Default value for DICT must be a dict, got {type(x).__name__}")

def validate_enum_field(x, values):
    if 'choices' not in values:
        raise ValueError("Field type ENUM requires the 'choices' attribute to be specified.")

    choices = values['choices']
    same_dtype, dtype_ = convert.is_same_dtype(choices, return_dtype=True) 
    if not same_dtype:
        raise ValueError(f"Field type ENUM requires all choices to be of the same type, got {choices}")
        
    if not isinstance(x, dtype_):
        raise ValueError(f"Default value for ENUM must be an instance of the {dtype_.__name__}, got {type(x).__name__}")


prompt_validators  ={
    FieldType.NUMERIC: validate_number_field,
    FieldType.BOOLEAN: validate_bool_field,
    FieldType.STRING: validate_str_field,
    FieldType.DATETIME: validate_datetime_field,
    FieldType.LIST: validate_list_field,
    FieldType.DICT: validate_dict_field,
    FieldType.ENUM: validate_enum_field
}


class BasePromptField(BaseComponent, ABC):
    name: str
    default: Any = None
    field_type: FieldType = FieldType.STRING
    choices: list[Any] | None = None
    processor: Optional[Callable[[Any], Any]] = None
    processor_args: list[Any] = []
    processor_kwargs: list[Any] = {}

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name : str = name

    @field_validator('default')
    def default_matches_field_type(cls, x, values):
        """Ensure the default value matches the specified field type."""
        try:
            if x is None:
                return
            elif 'field_type' in values:
                field_type = values['field_type']
                if field_type == FieldType.ENUM:
                    prompt_validators[field_type](x, values)
                else:
                    prompt_validators[field_type](x)
            else:
                raise ValueError(f"Field type must be specified for field {values}")
        except Exception as e:
            raise e

    def process(self, x=None):
        x = x or self.default
        if self.processor is None:
            return x
        return self.processor(x, *self.processor_args, **self.processor_kwargs)

class Input(BasePromptField):
    input_output: InputOutput = InputOutput.INPUT

class Output(BasePromptField):
    input_output: InputOutput = InputOutput.OUTPUT
