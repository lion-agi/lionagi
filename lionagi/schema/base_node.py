import json
import xml.etree.ElementTree as ET
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

import pandas as pd
from pydantic import AliasChoices, BaseModel, Field, field_serializer

from lionagi.util import SysUtil

T = TypeVar('T', bound='BaseComponent')



class BaseComponent(BaseModel):
    id_: str = Field(default_factory=lambda: str(SysUtil.create_id()), alias="node_id")
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="meta")
    content: Union[str, Dict[str, Any], None, Any] = Field(
        default=None,
        validation_alias=AliasChoices('text', 'page_content', 'chunk_content')
    )

    class Config:
        extra = 'allow'
        populate_by_name = True
        validate_assignment = True
        validate_return = True
        str_strip_whitespace = True

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        return cls(**data)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        try:
            data = json.loads(json_str, **kwargs)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string provided for deserialization.") from e

    @classmethod
    def from_pd_series(cls: Type[T], pd_series: pd.Series) -> T:
        dict_ = pd_series.to_dict()
        return cls(**dict_)

    @classmethod
    def from_xml(cls: Type[T], xml_str: str) -> T:
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

    def to_pd_series(self) -> pd.Series:
        return pd.Series(self.to_dict())

    def validate_content(self, schema: Dict[str, type]) -> bool:
        if not isinstance(self.content, Dict):
            return False
        return SysUtil.is_schema(self.content, schema)

    def clone(self):
        cls = self.__class__
        return cls(**self.to_dict())

    def __str__(self) -> str:
        content_preview = (str(self.content)[:75] + '...') if len(str(self.content)) > 75 else str(self.content)
        metadata_preview = str(self.metadata)[:75] + '...' if len(str(self.metadata)) > 75 else str(self.metadata)

        return (f"{self.__class__.__name__}(id={self.id_},"
                f"content='{content_preview}', metadata='{metadata_preview}'")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_json()})"

class BaseNode(BaseComponent):
    
    @property
    def metadata_keys(self) -> List[str]:
        return list(self.metadata.keys())

    def has_metadata_key(self, key: str) -> bool:
        return key in self.metadata

    def get_metadata(self, key: str, default=None) -> Any:
        return self.metadata.get(key, default)

    def change_metadata_key(self, old_key: str, new_key: str) -> bool:
        if old_key in self.metadata:
            SysUtil.change_dict_key(self.metadata, old_key=old_key, new_key=new_key)
            return True
        return False

    def pop_metadata(self, key: str, default: Optional[Any] = None) -> Any:
        return self.metadata.pop(key, default)

    def merge_metadata(self, additional_metadata: Dict[str, Any], overwrite: bool = False) -> None:
        if not overwrite:
            additional_metadata = ({
                k: v for k, v in additional_metadata.items()
                if k not in self.metadata
            })
        self.metadata.update(additional_metadata)

    def clear_metadata(self) -> None:
        self.metadata.clear()

    def filter_metadata(self, filter_func: Callable[[Any], bool]) -> Dict[str, Any]:
        return {k: v for k, v in self.metadata.items() if filter_func(v)}

    def validate_metadata(self, schema: Dict[str, Type]) -> bool:
        return SysUtil.is_schema(dict_=self.metadata, schema=schema)


class RelatableNode(BaseNode):
    
    related_nodes: List[str] = Field(default_factory=list)
    label: str | None = None

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

class BaseActionNode(BaseNode):
    func: Any
    schema_: dict
    manual: Any = None
    parser: Any = None


    @field_serializer('func')
    def serialize_func(self, func):
        return func.__name__