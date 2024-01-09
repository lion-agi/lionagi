# uses utils
import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, TypeVar, Type, List, Callable, Union
from pydantic import BaseModel, Field, AliasChoices

from lionagi.utils import (
    create_id, is_schema, change_dict_key, create_copy, 
    encrypt, decrypt, dict_to_xml
)

T = TypeVar('T', bound='BaseNode')


class BaseNode(BaseModel):
    """
    A foundational building block for representing a node in a graph-like structure.
    This class includes functionalities for serialization, metadata manipulation,
    content encryption/decryption, and utility methods.

    Attributes:
        id_ (str): Unique identifier for the node, aliased as 'node_id'.
        metadata (Dict[str, Any]): Dictionary of metadata related to the node.
        label (Optional[str]): Label categorizing or identifying the node.
        related_nodes (List[str]): Identifiers for nodes related to this node.
        content (Union[str, Dict[str, Any], None, Any]): Content of the node.
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

    # from-to [json, dict, xml]
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> T:
        """Creates a BaseNode instance from a dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        """Creates a BaseNode instance from a JSON string."""
        try:
            data = json.loads(json_str, **kwargs)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string provided for deserialization.") from e

    @classmethod
    def from_xml(cls, xml_str: str) -> T:
        """Creates a BaseNode instance from an XML string."""
        root = ET.fromstring(xml_str)
        data = cls._xml_to_dict(root)
        return cls(**data)

    def to_json(self) -> str:
        """Converts the BaseNode instance into a JSON string."""
        return self.model_dump_json(by_alias=True)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the BaseNode instance into a dictionary."""
        return self.model_dump(by_alias=True)
    
    def to_xml(self) -> str:
        """Converts the BaseNode instance into an XML string."""
        return dict_to_xml(self.to_dict())
    
    # Metadata manipulation methods
    def set_meta(self, metadata_: Dict[str, Any]) -> None:
        """Sets the metadata for the node."""
        self.metadata = metadata_
        
    def get_meta_key(self, key: str) -> Any:
        """Retrieves a specific metadata value by key."""
        return self.metadata.get(key)

    def change_meta_key(self, old_key: str, new_key: str) -> None:
        """Changes a metadata key from old_key to new_key."""
        change_dict_key(self.metadata,old_key=old_key, new_key=new_key)

    def delete_meta_key(self, key: str) -> None:
        """Deletes a metadata key from the node."""
        if key in self.metadata:
            del self.metadata[key]
            
    def merge_metadata(self, other_metadata: Dict[str, Any], overwrite: bool = True) -> None:
        """Merges another metadata dictionary into the node's metadata."""
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
        """Returns a list of all metadata keys."""
        return list(self.metadata.keys())

    def has_meta_key(self, key: str) -> bool:
        """Checks if a specific metadata key exists."""
        return key in self.metadata

    def filter_meta(self, filter_func: Callable[[Any], bool]) -> Dict[str, Any]:
        """Filters metadata based on a provided function."""
        return {k: v for k, v in self.metadata.items() if filter_func(v)}

    def apply_to_meta(self, apply_func: Callable[[Any], Any]) -> None:
        """Applies a function to each metadata value."""
        for key in self.metadata:
            self.metadata[key] = apply_func(self.metadata[key])
        
    def meta_schema_is_valid(self, schema: Dict[str, type]) -> bool:
        """Checks if the metadata matches a given schema."""
        return is_schema(dict_=self.metadata, schema=schema)

    def update_meta(self, **kwargs) -> None:
        """Updates metadata with the provided key-value pairs."""
        self.metadata.update(kwargs)

    # Encryption methods
    def encrypt_content(self, key: str) -> None:
        """Encrypts the content of the node."""
        self.content = encrypt(self.content, key)

    def decrypt_content(self, key: str) -> None:
        """Decrypts the content of the node."""
        self.content = decrypt(self.content, key)
        
    # Getters and setters
    def set_content(self, content: Optional[Any]) -> None:
        """Sets the content of the node."""
        self.content = content

    def get_content(self) -> Optional[Any]:
        """Retrieves the content of the node."""
        return self.content

    def set_id(self, id_: str) -> None:
        """Sets the ID of the node."""
        self.id_ = id_

    def get_id(self) -> str:
        """Retrieves the ID of the node."""
        return self.id_

    def add_related_node(self, node_id: str) -> None:
        """Adds a related node ID."""
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)

    def remove_related_node(self, node_id: str) -> None:
        """Removes a related node ID."""
        self.related_nodes = [id_ for id_ in self.related_nodes if id_ != node_id]

    # Utility methods
    def is_empty(self) -> bool:
        """Checks if the node is empty (no content and metadata)."""
        return not self.content and not self.metadata

    def has_label(self, label: str) -> bool:
        """Checks if the node has a specific label."""
        return self.label == label

    def is_metadata_key_present(self, key: str) -> bool:
        """Checks if a specific key is present in the metadata."""
        return key in self.metadata

    def copy(self, n: int = 1) -> Union[List[T], T]:
        """
        Creates one or multiple deep copies of the node.

        Parameters:
            n (int): Number of copies to create.

        Returns:
            Union[List[T], T]: A copy or list of copies of the node.
        """
        return create_copy(self, n)

    def data_equals(self, other: 'BaseNode') -> bool:
        """
        Checks if the node's data equals another node's data.

        Parameters:
            other (BaseNode): Another node to compare with.

        Returns:
            bool: True if data is equal, False otherwise.
        """
        return (
            self.content == other.content and
            self.metadata == other.metadata and
            self.related_nodes == other.related_nodes
        )

    def is_copy_of(self, other: 'BaseNode') -> bool:
        """
        Checks if the node is a copy of another node.

        Parameters:
            other (BaseNode): Another node to compare with.

        Returns:
            bool: True if it is a copy, False otherwise.
        """
        return (
            self.data_equals(other) and
            self is not other
        )

    def __eq__(self, other: 'BaseNode') -> bool:
        """
        Overrides the equality operator to compare nodes.

        Parameters:
            other (BaseNode): Another node to compare with.

        Returns:
            bool: True if nodes are equal, False otherwise.
        """
        return (self.id_ == other.id_ and self.data_equals(other))

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the BaseNode.

        Returns:
            str: A string representation of the BaseNode.
        """
        content_preview = (str(self.content)[:75] + '...') if len(str(self.content)) > 75 else str(self.content)
        return f"{self.__class__.__name__}(id={self.id_}, label={self.label}, content='{content_preview}')"

    def __repr__(self):
        """
        Official string representation of Message object.
        Utilizes the json representation of the object for clarity.
        """
        return f"{self.__class__.__name__}({self.to_json()})"
