from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Model(BaseModel):
    id: str = Field(
        ...,
        description="The model identifier, which can be referenced in the API endpoints.",
    )
    object: str = Field(
        "model", description="The object type, which is always 'model'."
    )
    created: int = Field(
        ..., description="The Unix timestamp (in seconds) when the model was created."
    )
    owned_by: str = Field(..., description="The organization that owns the model.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "gpt-3.5-turbo-instruct",
                "object": "model",
                "created": 1686935002,
                "owned_by": "openai",
            }
        }
    )


class ModelList(BaseModel):
    object: str = Field("list", description="The object type, which is always 'list'.")
    data: List[Model] = Field(..., description="The list of model objects.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "object": "list",
                "data": [
                    {
                        "id": "model-id-0",
                        "object": "model",
                        "created": 1686935002,
                        "owned_by": "organization-owner",
                    },
                    {
                        "id": "model-id-1",
                        "object": "model",
                        "created": 1686935002,
                        "owned_by": "organization-owner",
                    },
                    {
                        "id": "model-id-2",
                        "object": "model",
                        "created": 1686935002,
                        "owned_by": "openai",
                    },
                ],
            }
        }
    )


class DeleteModelResponse(BaseModel):
    id: str = Field(..., description="The ID of the deleted model.")
    object: str = Field(
        "model", description="The object type, which is always 'model'."
    )
    deleted: bool = Field(
        ..., description="Indicates whether the model was successfully deleted."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "ft:gpt-4o-mini:acemeco:suffix:abc123",
                "object": "model",
                "deleted": True,
            }
        }
    )


# API function signatures (these would be implemented elsewhere)


def list_models() -> ModelList:
    """Lists the currently available models, and provides basic information about each one."""
    ...


def retrieve_model(model_id: str) -> Model:
    """Retrieves a model instance, providing basic information about the model."""
    ...


def delete_fine_tuned_model(model_id: str) -> DeleteModelResponse:
    """Delete a fine-tuned model. Requires Owner role in the organization."""
    ...
