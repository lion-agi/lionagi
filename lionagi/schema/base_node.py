import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, TypeVar, Type, List, Callable, Union
from pydantic import BaseModel, Field, AliasChoices

from ..utils.sys_util import create_id, change_dict_key, is_schema
from ..utils.encrypt_util import EncrytionUtil as eu

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
        validate_return = True
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

    def to_xml(self) -> str:
        root = ET.Element(self.__class__.__name__)
        for attr, value in self.to_dict().items():
            child = ET.SubElement(root, attr)
            child.text = str(value)
        return ET.tostring(root, encoding='unicode')

    def validate_content(self, schema: Dict[str, type]) -> bool:
        if not isinstance(self.content, dict):
            return False
        return is_schema(self.content, schema)

    @property
    def meta_keys(self) -> List[str]:
        return list(self.metadata.keys())

    def has_meta_key(self, key: str) -> bool:
        return key in self.metadata

    def get_meta_key(self, key: str) -> Any:
        return self.metadata.get(key)

    def change_meta_key(self, old_key: str, new_key: str) -> bool:
        if old_key in self.metadata:
            change_dict_key(self.metadata, old_key=old_key, new_key=new_key)
            return True
        return False

    def delete_meta_key(self, key: str) -> bool:
        if key in self.metadata:
            del self.metadata[key]
            return True
        return False
            
    def merge_meta(self, other_metadata: Dict[str, Any], overwrite: bool = False) -> None:
        if not overwrite:
            other_metadata = ({
                k: v for k, v in other_metadata.items() 
                if k not in self.metadata
            })
        self.metadata.update(other_metadata)

    def clear_meta(self) -> None:
        self.metadata.clear()

    def filter_meta(self, filter_func: Callable[[Any], bool]) -> Dict[str, Any]:
        return {k: v for k, v in self.metadata.items() if filter_func(v)}

    def validate_meta(self, schema: Dict[str, type]) -> bool:
        return is_schema(dict_=self.metadata, schema=schema)

    def encrypt_content(self, key: str) -> None:
        self.content = eu.encrypt(self.content, key)

    def decrypt_content(self, key: str) -> None:
        self.content = eu.decrypt(self.content, key)

    def add_related_node(self, node_id: str) -> bool:
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)
            return True
        return False

    def remove_related_node(self, node_id: str) -> bool:
        if node_id in self.related_nodes:
            self.related_nodes.remove(node_id)
            return True
        return False

    def __str__(self) -> str:
        content_preview = (str(self.content)[:75] + '...') if len(str(self.content)) > 75 else str(self.content)
        metadata_preview = str(self.metadata)[:75] + '...' if len(str(self.metadata)) > 75 else str(self.metadata)
        related_nodes_preview = ', '.join(self.related_nodes[:3]) + ('...' if len(self.related_nodes) > 3 else '')
        return (f"{self.__class__.__name__}(id={self.id_}, label={self.label}, "
                f"content='{content_preview}', metadata='{metadata_preview}', "
                f"related_nodes=[{related_nodes_preview}])")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_json()})"



    # def is_empty(self) -> bool:
    #     return not self.content and not self.metadata

    # def copy(self, n: int = 1) -> Union[List[T], T]:
    #     return create_copy(self, n)

    # def data_equals(self, other: 'BaseNode') -> bool:
    #     return (
    #         self.content == other.content and
    #         self.metadata == other.metadata and
    #         self.related_nodes == other.related_nodes
    #     )

    # def is_copy_of(self, other: 'BaseNode') -> bool:
    #     return (
    #         self.data_equals(other) and
    #         self is not other
    #     )

    # def __eq__(self, other: 'BaseNode') -> bool:
    #     # return (self.id_ == other.id_ and self.data_equals(other))
    #     return self.id_ == other.id_
