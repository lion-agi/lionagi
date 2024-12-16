"""
Copyright 2024 HaiyangLi

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from lionagi.core.typing import FieldModel, NewModelParams
from lionagi.protocols.operatives.operative import Operative

from .action import (
    ACTION_REQUESTS_FIELD,
    ACTION_REQUIRED_FIELD,
    ACTION_RESPONSES_FIELD,
    ActionRequestModel,
    ActionResponseModel,
)
from .reason import REASON_FIELD, ReasonModel


class StepModel(BaseModel):
    """Model representing a single operational step with optional reasoning and actions."""

    title: str
    description: str
    reason: ReasonModel | None = REASON_FIELD.field_info
    action_requests: list[ActionRequestModel] = (
        ACTION_REQUESTS_FIELD.field_info
    )
    action_required: bool = ACTION_REQUIRED_FIELD.field_info
    action_responses: list[ActionResponseModel] = (
        ACTION_RESPONSES_FIELD.field_info
    )


class Step:
    """Utility class providing methods to create and manage Operative instances for steps."""

    @staticmethod
    def request_operative(
        *,
        operative_name: str | None = None,
        reason: bool = False,
        actions: bool = False,
        request_params: NewModelParams | None = None,
        parameter_fields: dict[str, FieldInfo] | None = None,
        base_type: type[BaseModel] | None = None,
        field_models: list[FieldModel] | None = None,
        exclude_fields: list[str] | None = None,
        new_model_name: str | None = None,
        field_descriptions: dict[str, str] | None = None,
        inherit_base: bool = True,
        config_dict: dict | None = None,
        doc: str | None = None,
        frozen: bool = False,
    ) -> Operative:
        """Creates an Operative instance configured for request handling.

        Args:
            operative_name (str, optional): Name of the operative.
            reason (bool, optional): Whether to include reason field.
            actions (bool, optional): Whether to include action fields.
            request_params (NewModelParams, optional): Parameters for the new model.
            parameter_fields (dict[str, FieldInfo], optional): Parameter fields for the model.
            base_type (type[BaseModel], optional): Base type for the model.
            field_models (list[FieldModel], optional): List of field models.
            exclude_fields (list[str], optional): List of fields to exclude.
            new_model_name (str | None, optional): Name of the new model.
            field_descriptions (dict[str, str], optional): Descriptions for the fields.
            inherit_base (bool, optional): Whether to inherit base.
            config_dict (dict | None, optional): Configuration dictionary.
            doc (str | None, optional): Documentation string.
            frozen (bool, optional): Whether the model is frozen.

        Returns:
            Operative: The configured operative instance.
        """

        field_models = field_models or []
        exclude_fields = exclude_fields or []
        field_descriptions = field_descriptions or {}
        if reason:
            field_models.append(REASON_FIELD)
        if actions:
            field_models.extend(
                [
                    ACTION_REQUESTS_FIELD,
                    ACTION_REQUIRED_FIELD,
                ]
            )
        request_params = request_params or NewModelParams(
            parameter_fields=parameter_fields,
            base_type=base_type,
            field_models=field_models,
            exclude_fields=exclude_fields,
            name=new_model_name,
            field_descriptions=field_descriptions,
            inherit_base=inherit_base,
            config_dict=config_dict,
            doc=doc,
            frozen=frozen,
        )
        return Operative(name=operative_name, request_params=request_params)

    @staticmethod
    def respond_operative(
        *,
        operative: Operative,
        additional_data: dict | None = None,
        response_params: NewModelParams | None = None,
        field_models: list[FieldModel] | None = None,
        frozen_response: bool = False,
        response_config_dict: dict | None = None,
        response_doc: str | None = None,
        exclude_fields: list[str] | None = None,
    ) -> Operative:
        """Updates the operative with response parameters and data.

        Args:
            operative (Operative): The operative instance to update.
            additional_data (dict | None, optional): Additional data to include in the response.
            response_params (NewModelParams | None, optional): Parameters for the response model.
            field_models (list[FieldModel] | None, optional): List of field models.
            frozen_response (bool, optional): Whether the response model is frozen.
            response_config_dict (dict | None, optional): Configuration dictionary for the response.
            response_doc (str | None, optional): Documentation string for the response.
            exclude_fields (list[str] | None, optional): List of fields to exclude.

        Returns:
            Operative: The updated operative instance.
        """

        additional_data = additional_data or {}
        field_models = field_models or []
        operative = Step._create_response_type(
            operative=operative,
            response_params=response_params,
            field_models=field_models,
            frozen_response=frozen_response,
            response_config_dict=response_config_dict,
            response_doc=response_doc,
            exclude_fields=exclude_fields,
        )

        data = operative.response_model.model_dump()
        data.update(additional_data or {})
        operative.response_model = operative.response_type.model_validate(data)
        return operative

    @staticmethod
    def _create_response_type(
        operative: Operative,
        response_params: NewModelParams | None = None,
        response_validators: dict | None = None,
        frozen_response: bool = False,
        response_config_dict: dict | None = None,
        response_doc: str | None = None,
        field_models: list[FieldModel] | None = None,
        exclude_fields: list[str] | None = None,
    ) -> Operative:
        """Internal method to create a response type for the operative.

        Args:
            operative (Operative): The operative instance.
            response_params (NewModelParams | None, optional): Parameters for the response model.
            response_validators (dict | None, optional): Validators for the response model.
            frozen_response (bool, optional): Whether the response model is frozen.
            response_config_dict (dict | None, optional): Configuration dictionary for the response.
            response_doc (str | None, optional): Documentation string for the response.
            field_models (list[FieldModel] | None, optional): List of field models.
            exclude_fields (list[str] | None, optional): List of fields to exclude.

        Returns:
            Operative: The operative instance with updated response type.
        """

        field_models = field_models or []

        if (
            hasattr(operative.request_type, "action_required")
            and operative.response_model.action_required
        ):
            field_models.extend(
                [
                    ACTION_RESPONSES_FIELD,
                    ACTION_REQUIRED_FIELD,
                    ACTION_REQUESTS_FIELD,
                ]
            )
        if hasattr(operative.request_type, "reason"):
            field_models.extend([REASON_FIELD])

        exclude_fields = exclude_fields or []
        exclude_fields.extend(operative.request_params.exclude_fields)

        operative.create_response_type(
            response_params=response_params,
            field_models=field_models,
            exclude_fields=exclude_fields,
            doc=response_doc,
            config_dict=response_config_dict,
            frozen=frozen_response,
            validators=response_validators,
        )
        return operative
