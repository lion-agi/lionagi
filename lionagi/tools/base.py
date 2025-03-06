# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import ClassVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    field_serializer,
    field_validator,
    model_validator,
)

from lionagi.operatives.action.tool import Tool
from lionagi.protocols.generic.element import IDType
from lionagi.protocols.graph.graph import Graph
from lionagi.protocols.graph.node import Node
from lionagi.utils import HashableModel


class LionTool(ABC):
    is_lion_system_tool: bool = True
    system_tool_name: str

    @abstractmethod
    def to_tool(self) -> Tool:
        pass


class ResourceCategory(str, Enum):
    FRAMEWORK = "framework"
    TEMPLATE = "template"
    UTILITY = "utility"
    PROMPT = "prompt"
    DOCUMENT = "document"
    CHUNK = "chunk"
    OTHER = "other"


class MetaModel(HashableModel):
    model_config = ConfigDict(
        extra="allow",
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )


class ResourceMeta(MetaModel):
    title: str | None = None
    domain: str | None = None
    version: str = Field(default="0.1.0", frozen=True)
    overview: str | None = None


class Resource(Node):
    meta_type: ClassVar[type[MetaModel]] = ResourceMeta
    content: JsonValue = None
    category: ResourceCategory = Field(
        default=ResourceCategory.OTHER, frozen=True
    )
    _meta_obj: BaseModel = None

    @property
    def meta_obj(self) -> BaseModel:
        if self._meta_obj is not None:
            return self._meta_obj
        return self.meta_type.model_validate(self.metadata)

    @meta_obj.setter
    def meta_obj(self, value: BaseModel):
        if not isinstance(value, self.meta_type):
            raise ValueError(
                f"Invalid metadata object type: {type(value)} "
                f"(expected: {self.meta_type})"
            )
        self._meta_obj = value

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


class Prompt(Resource):
    category: ResourceCategory = Field(
        default=ResourceCategory.PROMPT, frozen=True
    )


class Framework(Resource):
    category: ResourceCategory = Field(
        default=ResourceCategory.FRAMEWORK, frozen=True
    )


class Template(Resource):
    category: ResourceCategory = Field(
        default=ResourceCategory.TEMPLATE, frozen=True
    )


class Provider(ABC):
    
    name: str
    capabilities: tuple[str]
    
    
    def create_tool(self, capability: str, **kwargs) -> Tool:
        if str(capability).strip().lower() not in self.capabilities:
            raise ValueError(f"Capability not supported by provider {self.name}")
        return self._create_tool(capability, **kwargs)
    
    
    def _create_tool(self, capability: str, **kwargs) -> Tool:
        raise NotImplementedError("Method not implemented")
