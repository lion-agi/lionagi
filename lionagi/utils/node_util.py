import json
from typing import Any, Dict, Union
from .sys_util import create_id

from pydantic import BaseModel, Field

class BaseNode(BaseModel):
    """
    Represents the base structure of a graph node.

    Args:
        BaseModel (pydantic.BaseModel): Pydantic BaseModel class for data validation.

    Attributes:
        id_ (str): Unique node identifier, auto-generated using uuid4().
        label (Optional[str]): Optional label for the node.
        content (Union[str, Dict[str, Any], None]): Content of the node.
        metadata (Dict[str, Any]): Additional metadata about the node.
    """
    id_: str = Field(default_factory=lambda: str(create_id()), alias="node_id")
    label: str = None
    content: Union[str, Dict[str, Any], None] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__

    # to some structure
    def to_json(self) -> str:
        return json.dumps(self.model_dump(by_alias=True))

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True)

    # from some structure
    @classmethod
    def from_json(cls, json_str: str) -> "BaseNode":
        data = json.loads(json_str)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseNode":
        return cls(**data)

    # setters    
    def set_meta(self, **kwags) -> None:
        self.metadata.update(**kwags)
    
    def set_content(self, content: Union[str, Dict[str, Any], None]):
        self.content = content

    def set_id(self, id: str):
        self.id_ = id

    #getters
    def get_meta(self):
        return self.metadata
    
    def get_content(self):
        return self.content
    
    def get_id(self):
        return self.id_
    
    
class DataNode(BaseNode):


    def from_llama(self, data_):
        ...
        
    def to_llama(self):
        # to llama_index textnode
        ...
        
    def from_langchain(self, data_):
        ...
    
    def to_langchain(self):
        ...
