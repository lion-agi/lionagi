"""
This module defines the PromptTemplate and ScoredTemplate classes for creating and managing prompt templates.

The PromptTemplate class is a base class for creating prompt templates with input and output fields, validation,
and processing. The ScoredTemplate class extends the PromptTemplate class and adds fields for confidence score and reason.
"""

from typing import Any
from lionagi.libs import convert, func_call
from lionagi.core.schema.base_node import BaseComponent

from pydantic import Field
from .field_validator import validation_funcs


_non_prompt_words = [
    "id_",
    "node_id",
    "meta",
    "timestamp",
    "metadata",
    "signature",
    "task",
    "template_name",
]


class PromptTemplate(BaseComponent):
    """
    A base class for creating and managing prompt templates.

    Attributes:
        signature (str): The signature indicating the input and output fields.
        choices (dict[str, list[str]]): The choices to select from for each field.
        out_validation_kwargs (dict[str, Any]): The validation keyword arguments for output fields.
        in_validation_kwargs (dict[str, Any]): The validation keyword arguments for input fields.
        task (str | dict[str, Any] | None): The task to follow.
        fix_input (bool): Whether to fix input fields.
        fix_output (bool): Whether to fix output fields.
        template_name (str): The name of the prompt template.
        version (str | float | int): The version of the prompt template.
        description (dict | str | None): The description of the prompt template.
        input_fields (list[str]): The input fields of the prompt template.
        output_fields (list[str]): The output fields of the prompt template.

    Methods:
        __init__(self, template_name="default_prompt_template", version_=None, description_=None, task=None, **kwargs):
            Initializes a new instance of the PromptTemplate class.
        _validate_input_choices(self, fix_=fix_input):
            Validates the input choices based on the defined choices.
        _validate_output_choices(self, fix_=fix_output):
            Validates the output choices based on the defined choices.
        _get_input_output_fields(str_) -> tuple[list[str], list[str]]:
            Extracts the input and output fields from the signature string.
        instruction_context(self) -> str:
            Returns the instruction context based on the input fields.
        instruction(self) -> str:
            Returns the instruction based on the task and input/output fields.
        instruction_output_fields(self) -> dict[str, str]:
            Returns a dictionary mapping output fields to their descriptions.
        prompt_fields_annotation(self) -> dict[str, list[str]]:
            Returns a dictionary mapping prompt fields to their annotated types.
        _validate_field(self, k, v, choices=None, fix_=False, **kwargs) -> bool:
            Validates a single field based on its annotated type and choices.
        _process_input(self, fix_=False):
            Processes and validates the input fields.
        _process_response(self, out_, fix_=True):
            Processes and validates the output fields.
        in_(self) -> dict[str, Any]:
            Returns a dictionary mapping input fields to their values.
        out(self) -> dict[str, Any]:
            Returns a dictionary mapping output fields to their values.
        process(self, in_=None, out_=None):
            Processes and validates the input and output fields.
    """

    signature: str = Field("null", description="signature indicating inputs, outputs")
    choices: dict[str, list[str]] = Field(
        default_factory=dict, description="choices to select from"
    )
    out_validation_kwargs: dict[str, Any] = Field(
        default_factory=dict, description="validation kwargs for output"
    )
    in_validation_kwargs: dict[str, Any] = Field(
        default_factory=dict, description="validation kwargs for input"
    )
    task: str | dict[str, Any] | None = Field(None, description="task to follow")
    fix_input: bool = Field(True, description="whether to fix input")
    fix_output: bool = Field(True, description="whether to fix output")

    def __init__(
        self,
        template_name: str = "default_prompt_template",
        version_: str | float | int = None,
        description_: dict | str | None = None,
        task: str | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.template_name = template_name
        self.meta_insert(["version"], version_)
        self.meta_insert(["description"], description_ or "")
        self.task = task
        self.input_fields, self.output_fields = self._get_input_output_fields(
            self.signature
        )
        self.process(in_=True)

    def _validate_input_choices(self, fix_=fix_input):
        if len(self.choices) >= 1:
            for k, choices in self.choices.items():
                if k in self.input_fields and not self._validate_field(
                    k, getattr(self, k), choices, fix_
                ):
                    raise ValueError(
                        f"Invalid choice for field {k}: {getattr(self, k)} is not in {choices}"
                    )

    def _validate_output_choices(self, fix_=fix_output):
        if len(self.choices) >= 1:
            for k, choices in self.choices.items():
                if k in self.output_fields and not self._validate_field(
                    k, getattr(self, k), choices, fix_
                ):
                    raise ValueError(
                        f"Invalid choice for field {k}: {getattr(self, k)} is not in {choices}"
                    )

    @property
    def version(self):
        return self.metadata["version"]

    @version.setter
    def version(self, value):
        self.metadata["version"] = value

    @property
    def description(self):
        return self.metadata["description"]

    @description.setter
    def description(self, value):
        self.metadata["description"] = value

    @property
    def prompt_fields(self):
        return [
            _field for _field in self.property_keys if _field not in _non_prompt_words
        ]

    @staticmethod
    def _get_input_output_fields(str_):
        _inputs, _outputs = str_.split("->")

        _inputs = [convert.strip_lower(i) for i in _inputs.split(",")]
        _outputs = [convert.strip_lower(o) for o in _outputs.split(",")]

        return _inputs, _outputs

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
    def prompt_fields_annotation(self):
        dict_ = {i: self.model_fields[i].annotation for i in self.prompt_fields}
        for k, v in dict_.items():
            if "|" in str(v):
                v = str(v)
                v = v.split("|")
                dict_[k] = func_call.lcall(v, convert.strip_lower)
            else:
                dict_[k] = [v.__name__]

        return dict_

    def _validate_field(self, k, v, choices=None, fix_=False, **kwargs):

        str_ = self.prompt_fields_annotation[k]

        if choices:
            v_ = validation_funcs["enum"](v, choices=choices, fix_=fix_, **kwargs)
            if v_ not in choices:
                raise ValueError(f"{v} is not in chocies {choices}")
            setattr(self, k, v_)
            return True

        elif "bool" in str_:
            self.__setattr__(k, validation_funcs["bool"](v, fix_=fix_, **kwargs))
            return True

        elif "int" in str_ or "float" in str_:
            self.__setattr__(k, validation_funcs["number"](v, fix_=fix_, **kwargs))
            return True

        elif "str" in str_:
            self.__setattr__(k, validation_funcs["str"](v, fix_=fix_, **kwargs))
            return True

        return False

    def _process_input(self, fix_=False):
        kwargs = self.in_validation_kwargs.copy()
        for k, v in self.in_.items():
            if k not in kwargs:
                kwargs = {k: {}}

            try:
                if (
                    self.model_fields[k].json_schema_extra["choices"] is not None
                    and "choices" in self.model_fields[k].json_schema_extra
                ):
                    self.choices[k] = self.model_fields[k].json_schema_extra["choices"]
                    if self._validate_field(
                        k, v, choices=self.choices[k], fix_=fix_, **kwargs[k]
                    ):
                        continue
                    else:
                        raise ValueError(f"{k} has no choices")

            except Exception as e:
                if self._validate_field(k, v, fix_=fix_, **kwargs[k]):
                    continue
                else:
                    raise ValueError(f"failed to validate field {k}") from e

    def _process_response(self, out_, fix_=True):
        kwargs = self.out_validation_kwargs.copy()
        for k, v in out_.items():
            if k not in kwargs:
                kwargs = {k: {}}
            try:
                if (
                    self.model_fields[k].json_schema_extra["choices"] is not None
                    and "choices" in self.model_fields[k].json_schema_extra
                ):
                    self.choices[k] = self.model_fields[k].json_schema_extra["choices"]
                    if self._validate_field(
                        k, v, choices=self.choices[k], fix_=fix_, **kwargs[k]
                    ):
                        continue
                    else:
                        raise ValueError(f"{k} has no choices")

            except Exception as e:
                if self._validate_field(k, v, fix_=fix_, **kwargs[k]):
                    continue
                else:
                    raise ValueError(f"failed to validate field {k}") from e

    @property
    def in_(self):
        return {i: self.__getattribute__(i) for i in self.input_fields}

    @property
    def out(self):
        return {i: self.__getattribute__(i) for i in self.output_fields}

    def process(self, in_=None, out_=None):
        if in_:
            self._process_input(fix_=self.fix_input)
            self._validate_input_choices(fix_=self.fix_input)
        if out_:
            self._process_response(out_, fix_=self.fix_output)
            self._validate_output_choices(fix_=self.fix_output)
        return self


class ScoredTemplate(PromptTemplate):
    confidence_score: float | None = Field(
        -1,
        description="a numeric score between 0 to 1 formatted in num:0.2f",
    )
    reason: str | None = Field(
        default_factory=str, description="brief reason for the given output"
    )


# class Weather(PromptTemplate):
#     sunny: bool = Field(True, description="true if the weather is sunny outside else false")
#     rainy: bool = Field(False, description="true if it is raining outside else false")
#     play1: bool = Field(True, description="conduct play1")
#     play2: bool = Field(False, description="conduct play2")
#     signature: str = Field("sunny, rainy -> play1, play2")

# predictor = Weather(
#     template_name="predictor",
#     task_ = "decides to conduct one of play1 and play2",
#     version_=0.1,
#     description_="predicts the weather and decides play",
#     signature = "sunny, play1 -> play2"
#     )

# predictor.to_instruction()
