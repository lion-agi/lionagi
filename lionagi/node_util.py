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
    content: Union[str, Dict[str, Any], None] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def class_name(cls) -> str:
        """
        Get the class name.

        Returns:
            str: Name of the class.
        """
        return cls.__name__

    def to_json(self) -> str:
        """
        Serialize the node instance to a JSON string.

        Returns:
            str: JSON string representing the node instance.
        """
        return json.dumps(self.model_dump(by_alias=True))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representing the node instance.
        """
        return self.model_dump(by_alias=True)

    @classmethod
    def from_json(cls, json_str: str) -> "BaseNode":
        """
        Create a BaseNode instance from a JSON string.

        Args:
            json_str (str): JSON string to deserialize.

        Returns:
            BaseNode: An instance of `BaseNode`.
        """
        data = json.loads(json_str)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseNode":
        """
        Create a BaseNode instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary of node data.

        Returns:
            BaseNode: An instance of `BaseNode`.
        """
        return cls(**data)
    
    def set_meta(self, **kwags) -> None:
        """
        Add a metadata key-value pair to the node.

        Args:
            key (str): Key of the metadata.
            value (Any): Value of the metadata.
        """
        
        self.metadata.update(**kwags)
        
    def get_meta(self):
        """
        Get the metadata of the node.

        Returns:
            Dict[str, Any]: Dictionary of metadata.
        """
        return self.metadata
    
    def set_content(self, content):
        self.content = content
        
    def get_content(self):
        return self.content

class DataNode(BaseNode):
    """
    Represents a data node.

    Args:
        BaseNode (lionagi.nodes.base.BaseNode): BaseNode class for data validation.
    """
    pass
