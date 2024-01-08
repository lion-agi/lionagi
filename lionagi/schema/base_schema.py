import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, TypeVar, Type, List, Callable, Union
from pydantic import BaseModel, Field, AliasChoices

from ..utils.sys_util import create_id, is_schema, dict_to_xml, change_dict_key

T = TypeVar('T', bound='BaseNode')


class BaseNode(BaseModel):
    """
    BaseNode: A foundational building block for representing a node in a graph-like structure.

    Attributes:
        id_ (str):
            Unique identifier for the node, aliased as 'node_id'.
        content (Optional[Any]):
            Content or value the node represents.
        metadata (Dict[str, Any]):
            A dictionary of metadata related to the node.
        label (Optional[str]):
            A label for categorizing or identifying the node.
        related_nodes (List[str]):
            A list of identifiers for nodes related to this node.
    """
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

    # ----------------- from-to [json, dict, xml] ----------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> T:
        """Creates a node instance from a dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        """Creates a node instance from a JSON string."""
        try:
            data = json.loads(json_str, **kwargs)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string provided for deserialization.") from e

    @classmethod
    def from_xml(cls, xml_str: str) -> 'BaseNode':
        """
        Creates a BaseNode instance from an XML string.

        Parameters:
            xml_str (str): The XML string representing a BaseNode.

        Returns:
            BaseNode: An instance of BaseNode created from the XML data.
        """
        root = ET.fromstring(xml_str)
        data = cls._xml_to_dict(root)
        return cls(**data)

    def to_json(self) -> str:
        """Converts the node instance into JSON string representation."""
        return self.model_dump_json(by_alias=True)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the node instance into a dictionary representation."""
        return self.model_dump(by_alias=True)
    
    def to_xml(self) -> str:
        """Converts the node instance into XML string representation."""
        return dict_to_xml(self.to_dict())
    

    # -------------------------- metadata manipulation -----------------------------------
    def set_meta(self, metadata_: Dict[str, Any]) -> None:
        self.metadata = metadata_
        
    def get_meta_key(self, key: str) -> Any:
        """Retrieves a value from the metadata by key."""
        return self.metadata.get(key)

    def change_meta_key(self, old_key: str, new_key: str) -> None:
        """Updates or adds a key-value pair in the metadata."""
        change_dict_key(self.metadata,old_key=old_key, new_key=new_key)

    def delete_meta_key(self, key: str) -> None:
        """Deletes a key from the metadata."""
        if key in self.metadata:
            del self.metadata[key]
            
    def merge_metadata(self, other_metadata: Dict[str, Any], overwrite: bool = True) -> None:
        """Merges another dictionary into the node's metadata."""
        if not overwrite:
            other_metadata = ({
                k: v for k, v in other_metadata.items() 
                if k not in self.metadata
            })
        self.metadata.update(other_metadata)

    def clear_metadata(self) -> None:
        """Clears all metadata from the node."""
        self.metadata.clear()

    @property
    def meta_keys(self) -> List[str]:
        """Returns a list of all keys currently in the metadata."""
        return list(self.metadata.keys())

    def has_meta_key(self, key: str) -> bool:
        """Checks if a certain key exists in the metadata."""
        return key in self.metadata

    def filter_meta(self, filter_func: Callable[[Any], bool]) -> Dict[str, Any]:
        """Filters the metadata based on a provided function or criteria."""
        return {k: v for k, v in self.metadata.items() if filter_func(v)}

    def apply_to_meta(self, apply_func: Callable[[Any], Any]) -> None:
        """Applies a function to the metadata or to specific items within the metadata."""
        for key in self.metadata:
            self.metadata[key] = apply_func(self.metadata[key])
        
    def meta_schema_is_valid(self, schema: Dict[str, type]) -> bool:
        """Validates the metadata structure against a given schema."""
        return is_schema(dict_=self.metadata, schema=schema)

    def update_meta(self, **kwargs) -> None:
        self.metadata.update(kwargs)


    # -------------------------- getters / setters ----------------------------
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


    def __eq__(self, other: 'BaseNode') -> bool:
        """
        Check if this node is equal to another node in terms of data.
        """
        return (self.id_ == other.id_ and self.data_equals(other))


    
    # Utility Methods
    def is_empty(self) -> bool:
        return not self.content and not self.metadata

    def has_label(self, label: str) -> bool:
        return self.label == label

    def is_metadata_key_present(self, key: str) -> bool:
        return key in self.metadata

    def copy(self, deep: bool = True, n: int = 1) -> Union[List[T], T]:
        """
        Creates a copy of the node instance.

        Parameters:
            deep (bool): Whether to make a deep copy.

            n (int): Number of copies to create.

        Returns:
            A copy or list of copies of the BaseNode instance.
        """
        copies = [self.copy(deep=deep) for _ in range(n)]
        return copies[0] if n == 1 else copies

    def data_equals(self, other: 'BaseNode') -> bool:
        """Check if this node is equal to another node in terms of data."""
        return (
            self.content == other.content and
            self.metadata == other.metadata and
            self.related_nodes == other.related_nodes
        )

    def is_copy_of(self, other: 'BaseNode') -> bool:
        """
        Check if this node is a deep copy of another node.
        """
        return (
            self.data_equals(other) and
            self is not other
        )



class DataNode(BaseNode):

    def to_llama_index(self, **kwargs):
        # to llama_index textnode
        from lionagi.bridge.llama_index import to_llama_index_textnode
        return to_llama_index_textnode(self, **kwargs)

    def to_langchain(self, **kwargs):
        # to langchain document
        from lionagi.bridge.langchain import to_langchain_document
        return to_langchain_document(self, **kwargs)

    @classmethod
    def from_llama_index(cls, llama_node: Any, **kwargs):
        llama_dict = llama_node.to_dict(**kwargs)
        return cls.from_dict(llama_dict)

    @classmethod
    def from_langchain(cls, lc_doc: Any):
        info_json = lc_doc.to_json()
        info_node = {'lc_id': info_json['id']}
        info_node = {**info_node, **info_json['kwargs']}
        return cls(**info_node)

    # def __repr__(self) -> str:
    #     return f"DataNode(id={self.id_}, content={self.content}, metadata={self.metadata}, label={self.label})"

    # def __str__(self) -> str:
    #     return f"DataNode(id={self.id_}, label={self.label})"


class File(DataNode):

    ...
    

class Chunk(DataNode):

    ...    

    


