from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    field_serializer,
    field_validator,
)

from lionagi.protocols.graph.node import Node


class ResourceCategory(str, Enum):
    DOCUMENT = "document"
    CHUNK = "chunk"
    FRAMEWORK = "framework"
    TEMPLATE = "template"
    PROMPT = "prompt"
    UTILITY = "utility"
    OTHER = "other"


class ResourceMeta(BaseModel):

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )
    title: str | None = None
    version: str = Field(default="0.1.0", frozen=True)

    @property
    def keys(self):
        return set(self.model_fields.keys())


class Resource(Node):
    content: JsonValue = None
    category: ResourceCategory = Field(
        default=ResourceCategory.OTHER, frozen=True
    )

    @property
    def meta_obj(self) -> ResourceMeta:
        return ResourceMeta.model_validate(self.metadata)

    @field_serializer("category")
    def _serialize_resource_category(self, value: ResourceCategory) -> str:
        if isinstance(value, ResourceCategory):
            return value.value
        return str(value)

    @field_validator("category", mode="before")
    def _validate_resource_category(cls, value: str) -> ResourceCategory:
        if isinstance(value, ResourceCategory):
            return value
        if isinstance(value, str):
            return ResourceCategory(value)
        raise ValueError(f"Invalid resource category: {str(value)}")
