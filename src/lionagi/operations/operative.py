# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Operative class for handling request-response model validation and transformation.
Provides flexible model creation and validation with automatic retry capability.
"""

from typing import Any

from pydantic import BaseModel, Field, PrivateAttr, model_validator
from pydantic.fields import FieldInfo
from typing_extensions import Self

from lionagi.libs.parse.types import to_json, validate_keys
from lionagi.protocols.models import FieldModel
from lionagi.utils import UNDEFINED

from .model_params import ModelParams

__all__ = ("Operative",)


class Operative(BaseModel):
    """
    Handles request-response model validation and transformation.
    Manages model creation, validation rules, and response parsing.
    """

    name: str | None = None

    request_params: ModelParams | None = None
    request_type: type[BaseModel] | None = Field(
        default=None,
        alias="response_format",
        description="the structure for LLM to respond as",
    )

    response_params: ModelParams | None = None
    response_type: type[BaseModel] | None = Field(
        default=None,
        description="the final delivery structure for the operative",
    )
    response_model: BaseModel | None = None
    response_str_dict: dict | str | None = None

    fill_mapping: dict[str, Any] | None = None
    auto_retry_parse: bool = True
    max_retries: int = 3
    _should_retry: bool = PrivateAttr(default=None)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        """Initialize request type and name if not provided."""
        if self.request_type is None:
            self.request_type = self.request_params.create_new_model()
        if self.name is None:
            self.name = self.request_params.name or self.request_type.__name__
        return self

    def raise_validate_pydantic(self, text: str) -> None:
        """
        Strict validation of text against request type model.
        Raises exception on validation failure.
        """
        d_ = to_json(text, fuzzy_parse=True)
        if isinstance(d_, list | tuple) and len(d_) == 1:
            d_ = d_[0]
        try:
            d_ = validate_keys(
                d_, self.request_type.model_fields, handle_unmatched="raise"
            )
            d_ = {k: v for k, v in d_.items() if v != UNDEFINED}
            self.response_model = self.request_type.model_validate(d_)
            self._should_retry = False
        except Exception:
            self.response_str_dict = d_
            self._should_retry = True

    def force_validate_pydantic(self, text: str):
        """
        Force validation of text against request type model.
        Handles unmatched fields without raising exceptions.
        """
        d_ = to_json(text, fuzzy_parse=True)
        if isinstance(d_, list | tuple) and len(d_) == 1:
            d_ = d_[0]
        d_ = validate_keys(
            d_,
            self.request_type.model_fields,
            handle_unmatched="force",
            fill_mapping=self.fill_mapping,
        )
        d_ = {k: v for k, v in d_.items() if v != UNDEFINED}
        self.response_model = self.request_type.model_validate(d_)
        self._should_retry = False

    def update_response_model(
        self, text: str | None = None, data: dict | None = None
    ) -> BaseModel | dict | str | None:
        """
        Update response model from text or data input.
        Attempts validation with retry on failure.

        Args:
            text: Input text to parse and validate
            data: Direct data to update model

        Returns:
            Updated response model or raw data
        """
        if text is None and data is None:
            raise ValueError("Either text or data must be provided.")

        if text:
            self.response_str_dict = text
            try:
                self.raise_validate_pydantic(text)
            except Exception:
                self.force_validate_pydantic(text)

        if data and self.response_type:
            d_ = self.response_model.model_dump()
            d_.update(data)
            self.response_model = self.response_type.model_validate(d_)

        if not self.response_model and isinstance(
            self.response_str_dict, list
        ):
            try:
                self.response_model = [
                    self.request_type.model_validate(d_)
                    for d_ in self.response_str_dict
                ]
            except Exception:
                pass

        return self.response_model or self.response_str_dict

    def create_response_type(
        self,
        response_params: ModelParams | None = None,
        field_models: list[FieldModel] | None = None,
        parameter_fields: dict[str, FieldInfo] | None = None,
        exclude_fields: list[str] | None = None,
        field_descriptions: dict[str, str] | None = None,
        inherit_base: bool = True,
        config_dict: dict | None = None,
        doc: str | None = None,
        frozen: bool = False,
        validators: dict | None = None,
    ) -> None:
        """
        Create new response type with specified parameters.
        Configures model validation and structure.

        Args:
            response_params: Model parameters or None for defaults
            field_models: Custom field definitions
            parameter_fields: Field configurations
            exclude_fields: Fields to omit
            field_descriptions: Field documentation
            inherit_base: Whether to inherit base model
            config_dict: Model configuration
            doc: Model documentation
            frozen: Whether model is immutable
            validators: Custom validation rules
        """
        self.response_params = response_params or ModelParams(
            parameter_fields=parameter_fields,
            field_models=field_models,
            exclude_fields=exclude_fields,
            field_descriptions=field_descriptions,
            inherit_base=inherit_base,
            config_dict=config_dict,
            doc=doc,
            frozen=frozen,
            base_type=self.request_params.base_type,
        )
        if validators and isinstance(validators, dict):
            self.response_params._validators.update(validators)

        self.response_type = self.response_params.create_new_model()


# File: lionagi/protocols/operative.py
