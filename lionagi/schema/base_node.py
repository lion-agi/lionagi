# uses utils
import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, TypeVar, Type, List, Callable, Union
from pydantic import BaseModel, Field, AliasChoices

from lionagi.utils.sys_util import create_id, change_dict_key, _is_schema, create_copy
from lionagi.utils.encrypt_util import EncrytionUtil as eu

T = TypeVar('T', bound='BaseNode')


class BaseNode(BaseModel):
    id_: str = Field(default_factory=lambda: str(create_id()), alias="node_id")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    label: Optional[str] = None
    related_nodes: List[str] = Field(default_factory=list)
    content: Union[str, Dict[str, Any], None, Any] = Field(
        default=None, validation_alias=AliasChoices('text', 'page_content', 'chunk_content')
    )
    
    class Config:
        extra = 'allow'
        populate_by_name = True
        validate_assignment = True
        str_strip_whitespace = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> T:
        return cls(**data)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        try:
            data = json.loads(json_str, **kwargs)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string provided for deserialization.") from e

    @classmethod
    def from_xml(cls, xml_str: str) -> T:
        root = ET.fromstring(xml_str)
        data = cls._xml_to_dict(root)
        return cls(**data)

    def to_json(self) -> str:
        return self.model_dump_json(by_alias=True)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True)
    
    def set_meta(self, metadata_: Dict[str, Any]) -> None:
        self.metadata = metadata_
        
    def get_meta_field(self, key: str) -> Any:
        return self.metadata.get(key)

    def change_meta_key(self, old_key: str, new_key: str) -> None:
        change_dict_key(self.metadata,old_key=old_key, new_key=new_key)

    def delete_meta_field(self, key: str) -> None:
        if key in self.metadata:
            del self.metadata[key]
            
    def merge_meta(self, other_metadata: Dict[str, Any], overwrite: bool = True) -> None:
        if not overwrite:
            other_metadata = ({
                k: v for k, v in other_metadata.items() 
                if k not in self.metadata
            })
        self.metadata.update(other_metadata)

    def clear_meta(self) -> None:
        self.metadata.clear()

    @property
    def meta_keys(self) -> List[str]:
        return list(self.metadata.keys())

    def has_meta_key(self, key: str) -> bool:
        return key in self.metadata

    def filter_meta(self, filter_func: Callable[[Any], bool]) -> Dict[str, Any]:
        return {k: v for k, v in self.metadata.items() if filter_func(v)}

    def apply_to_meta(self, apply_func: Callable[[Any], Any]) -> None:
        for key in self.metadata:
            self.metadata[key] = apply_func(self.metadata[key])
        
    def meta_schema_is_valid(self, schema: Dict[str, type]) -> bool:
        return _is_schema(dict_=self.metadata, schema=schema)

    def update_meta(self, **kwargs) -> None:
        self.metadata.update(kwargs)

    def encrypt_content(self, key: str) -> None:
        self.content = eu.encrypt(self.content, key)

    def decrypt_content(self, key: str) -> None:
        self.content = eu.decrypt(self.content, key)
        
    def set_content(self, content: Optional[Any]) -> None:
        self.content = content

    def get_content(self) -> Optional[Any]:
        return self.content

    def set_id(self, id_: str) -> None:
        self.id_ = id_

    def get_id(self) -> str:
        return self.id_

    def add_related_node(self, node_id: str) -> None:
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)

    def remove_related_node(self, node_id: str) -> None:
        self.related_nodes = [id_ for id_ in self.related_nodes if id_ != node_id]

    def is_empty(self) -> bool:
        return not self.content and not self.metadata

    def has_label(self, label: str) -> bool:
        return self.label == label

    def is_metadata_key_present(self, key: str) -> bool:
        return key in self.metadata

    def copy(self, n: int = 1) -> Union[List[T], T]:
        return create_copy(self, n)

    def data_equals(self, other: 'BaseNode') -> bool:
        return (
            self.content == other.content and
            self.metadata == other.metadata and
            self.related_nodes == other.related_nodes
        )

    def is_copy_of(self, other: 'BaseNode') -> bool:
        return (
            self.data_equals(other) and
            self is not other
        )

    def __eq__(self, other: 'BaseNode') -> bool:
        return (self.id_ == other.id_ and self.data_equals(other))

    def __str__(self) -> str:
        content_preview = (str(self.content)[:75] + '...') if len(str(self.content)) > 75 else str(self.content)
        return f"{self.__class__.__name__}(id={self.id_}, label={self.label}, content='{content_preview}')"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_json()})"
