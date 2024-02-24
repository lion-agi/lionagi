from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Callable
import pandas as pd

from lionagi.util.sys_util import SysUtil
from lionagi.util import create_id

import json
import xml.etree.ElementTree as ET

from pydantic import BaseModel, Field, AliasChoices

T = TypeVar('T', bound='BaseComponent')


class BaseComponent(BaseModel):
    id_: str = Field(default_factory=lambda: str(create_id()), alias="node_id")
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








