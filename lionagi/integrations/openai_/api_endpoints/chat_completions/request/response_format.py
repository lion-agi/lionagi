import warnings
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, model_validator

# Suppress the specific warning about field name shadowing
warnings.filterwarnings(
    "ignore",
    message='Field name "schema" in "JSONSchema" '
    'shadows an attribute in parent "BaseModel"',
)


class JSONSchema(BaseModel):
    description: str | None = Field(
        None,
        description=(
            "A description of what the response format is for, used by the "
            "model to determine how to respond in the format."
        ),
    )

    name: str = Field(
        max_length=64,
        pattern="^[a-zA-Z0-9_-]+$",
        description=(
            "The name of the response format. Must be a-z, A-Z, 0-9, or "
            "contain underscores and dashes, with a maximum length of 64."
        ),
    )

    schema: dict[str, Any] | None = Field(
        None,
        description="The schema for the response "
        "format, described as a JSON Schema object.",
    )

    strict: bool | None = Field(
        False,
        description=(
            "Whether to enable strict schema adherence when generating the "
            "output. If set to true, the model will always follow the exact "
            "schema defined in the `schema` field. Only a subset of JSON "
            "Schema is supported when `strict` is `true`."
        ),
    )


class ResponseFormat(BaseModel):
    type: Literal["text", "json_object", "json_schema"] = Field(
        description="The type of response format being defined."
    )
    json_schema: JSONSchema | None = Field(
        None,
        description=(
            "The JSON schema to use when type is 'json_schema'. Required "
            "when type is 'json_schema'."
        ),
    )

    @model_validator(mode="after")
    def validate_response_format(self) -> "ResponseFormat":
        if self.type == "json_schema" and not self.json_schema:
            raise ValueError(
                "json_schema is required when type is 'json_schema'"
            )
        if self.type != "json_schema" and self.json_schema:
            raise ValueError(
                "json_schema should only be set when type is 'json_schema'"
            )
        return self
