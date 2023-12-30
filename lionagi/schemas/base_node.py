import json
import copy
import uuid
from typing import Any, Dict, Optional, Union, TypeVar, Type, List

from pydantic import BaseModel, Field, validator

T = TypeVar('T', bound='BaseNode')

class BaseNode(BaseModel):
    id_: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="node_id")
    content: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    label: Optional[str] = None
    related_nodes: List[str] = Field(default_factory=list)

    class Config:
        validate_assignment = True
        anystr_strip_whitespace = True
        json_encoders = {
            # Custom encoders for specific types can be placed here
        }

    @validator('*', pre=True, each_item=False)
    def non_empty(cls, v):
        if isinstance(v, (str, list, dict)) and not v:
            raise ValueError("Field must not be empty")
        return v

    def to_json(self) -> str:
        return self.model_dump_json(by_alias=True)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        try:
            data = json.loads(json_str, **kwargs)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string provided for deserialization.") from e


    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'T':
        return cls(**data)

    def deep_copy(self) -> 'BaseNode':
        return self.model_copy(deep=True)

    def merge_metadata(self, other_metadata: Dict[str, Any], overwrite: bool = True) -> None:
        if not overwrite:
            other_metadata = {k: v for k, v in other_metadata.items() if k not in self.metadata}
        self.metadata.update(other_metadata)

    def set_meta(self, metadata_: Dict[str, Any]) -> None:
        self.metadata = metadata_

    def get_meta(self) -> Dict[str, Any]:
        return self.metadata

    def set_content(self, content: Optional[Any]) -> None:
        self.content = content

    def get_content(self) -> Optional[Any]:
        return self.content

    def set_id(self, id_: str) -> None:
        self.id_ = id_

    def get_id(self) -> str:
        return self.id_

    def update_meta(self, **kwargs) -> None:
        self.metadata.update(kwargs)

    def add_related_node(self, node_id: str) -> None:
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)

    def remove_related_node(self, node_id: str) -> None:
        self.related_nodes = [id_ for id_ in self.related_nodes if id_ != node_id]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseNode):
            return NotImplemented
        return self.model_dump() == other.model_dump()

    def __str__(self) -> str:
        return f"BaseNode(id={self.id_}, label={self.label})"

    def __repr__(self) -> str:
        return f"BaseNode(id={self.id_}, content={self.content}, metadata={self.metadata}, label={self.label})"
    
    # Utility Methods
    def is_empty(self) -> bool:
        return not self.content and not self.metadata

    def has_label(self, label: str) -> bool:
        return self.label == label

    def is_metadata_key_present(self, key: str) -> bool:
        return key in self.metadata
