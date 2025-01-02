# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from lionagi.libs.validate.fuzzy_validate_mapping import fuzzy_validate_mapping
from lionagi.utils import UNDEFINED

from .models.field_model import FieldModel
from .models.model_params import ModelParams


class Operative:

    def __init__(
        self,
        name: str | None = None,
        request_params: ModelParams | None = None,
        response_params: ModelParams | None = None,
        max_retries: int = 3,
    ):
        self.request_params = request_params
        self.response_params = response_params
        self.request_type = None
        self.response_type = None
        self.max_retries = max_retries
        self.name = name
        if self.request_type is None:
            self.request_type = self.request_params.create_new_model()
        if self.name is None:
            self.name = self.request_params.name or self.request_type.__name__
        self.response_model = None
        self.response_str_dict = None

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

    def fuzzy_validate_pydantic(
        self,
        text: str,
        similarity_algo="jaro_winkler",
        similarity_threshold: float = 0.85,
        fuzzy_match: bool = True,
        handle_unmatched: Literal[
            "ignore", "raise", "remove", "fill", "force"
        ] = "force",
        fill_value: Any = UNDEFINED,
        fill_mapping: dict[str, Any] | None = None,
        strict: bool = False,
        suppress_conversion_errors: bool = False,
    ) -> None:
        d_ = fuzzy_validate_mapping(
            text,
            self.request_type.model_fields,
            similarity_algo=similarity_algo,
            similarity_threshold=similarity_threshold,
            fuzzy_match=fuzzy_match,
            handle_unmatched=handle_unmatched,
            fill_value=fill_value,
            fill_mapping=fill_mapping,
            strict=strict,
            suppress_conversion_errors=suppress_conversion_errors,
        )
        d_ = {k: v for k, v in d_.items() if v != UNDEFINED}
        try:
            return self.request_type.model_validate(d_)
        except Exception:
            return d_

    def update_response_model(
        self,
        text: str | None = None,
        data: dict | None = None,
        response_model: BaseModel | None = None,
        **kwargs,
    ) -> BaseModel | dict | str | None:
        """Updates the response model based on the provided text or data.

        Args:
            text (str, optional): The text to parse and validate.
            data (dict, optional): The data to update the response model with.

        Returns:
            BaseModel | dict | str | None: The updated response model or raw data.

        Raises:
            ValueError: If neither text nor data is provided.
        """
        if text is None and data is None:
            raise ValueError("Either text or data must be provided.")

        if text:
            return self.fuzzy_validate_pydantic(text, **kwargs)

        if data and self.response_type:
            if not response_model:
                raise ValueError("Response model must be provided.")
            d_ = response_model.model_dump()
            d_.update(data)
            response_model = self.response_type.model_validate(d_)

        if not response_model and isinstance(self.response_str_dict, list):
            try:
                self.response_model = [
                    self.request_type.model_validate(d_)
                    for d_ in self.response_str_dict
                ]
            except Exception:
                pass

        return self.response_model or self.response_str_dict
