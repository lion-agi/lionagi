import json
from typing import Any, Dict, Optional, TypeVar, Type, List, Callable, Union
from pydantic import BaseModel, Field, AliasChoices

from ..utils.sys_util import create_id

T = TypeVar('T', bound='BaseNode')


class BaseNode(BaseModel):
    """
    BaseNode: A foundational building block for representing a node in a graph-like structure.

    Attributes:
        id_ (str): Unique identifier for the node, aliased as 'node_id'.
        content (Optional[Any]): Content or value the node represents.
        metadata (Dict[str, Any]): A dictionary of metadata related to the node.
        label (Optional[str]): A label for categorizing or identifying the node.
        related_nodes (List[str]): A list of identifiers for nodes related to this node.
    """
    id_: str = Field(default_factory=lambda: str(create_id()), alias="node_id")
    content: Union[str, Dict[str, Any], None, Any] = Field(default=None,
                                                           validation_alias=AliasChoices('text', 'page_content', 'chunk_content'))
    metadata: Dict[str, Any] = Field(default_factory=dict)
    label: Optional[str] = None
    related_nodes: List[str] = Field(default_factory=list)

    class Config:
        extra = 'allow'
        populate_by_name = True
        validate_assignment = True
        str_strip_whitespace = True

    def to_json(self) -> str:
        """Converts the node instance into JSON string representation."""
        return self.model_dump_json(by_alias=True)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        """
        Creates a node instance from a JSON string.

        Args:
            json_str (str): The JSON string representing a node.
            **kwargs: Additional keyword arguments to pass to json.loads.

        Returns:
            An instance of BaseNode.

        Raises:
            ValueError: If the provided string is not valid JSON.
        """
        try:
            data = json.loads(json_str, **kwargs)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string provided for deserialization.") from e

    def to_dict(self) -> Dict[str, Any]:
        """Converts the node instance into a dictionary representation."""
        return self.model_dump(by_alias=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> T:
        """Creates a node instance from a dictionary."""
        return cls(**data)

    def copy(self, deep: bool = True, n: int = 1) -> T:
        """
        Creates a copy of the node instance.

        Args:
            deep (bool): Whether to make a deep copy.
            n (int): Number of copies to create.

        Returns:
            A copy or list of copies of the BaseNode instance.
        """
        copies = [self.copy(deep=deep) for _ in range(n)]
        return copies[0] if n == 1 else copies

    def merge_metadata(self, other_metadata: Dict[str, Any], overwrite: bool = True) -> None:
        """
        Merges another metadata dictionary into the node's metadata.

        Args:
            other_metadata (Dict[str, Any]): The metadata to merge in.
            overwrite (bool): Whether to overwrite existing keys in the metadata.
        """
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
        if not isinstance(other, T):
            return NotImplemented
        return self.model_dump() == other.model_dump()

    # def __str__(self) -> str:
    #     """Returns a simple string representation of the BaseNode."""
    #     return f"BaseNode(id={self.id_}, label={self.label})"

    # def __repr__(self) -> str:
    #     """Returns a detailed string representation of the BaseNode."""
    #     return f"BaseNode(id={self.id_}, content={self.content}, metadata={self.metadata}, label={self.label})"
    
    # Utility Methods
    def is_empty(self) -> bool:
        return not self.content and not self.metadata

    def has_label(self, label: str) -> bool:
        return self.label == label

    def is_metadata_key_present(self, key: str) -> bool:
        return key in self.metadata


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

    
class Message(BaseNode):
    """
    Message: A specialized type of BaseNode for handling messages.

    This class represents a message node, extending the BaseNode with additional
    attributes specific to messages, such as role and name, and provides methods
    for message-specific operations.

    Attributes:
        role (Optional[str]): The role of the message, e.g., 'sender', 'receiver'.
        name (Optional[str]): The name associated with the message, e.g., a user name or system name.
    """
    
    role: Optional[str] = None
    name: Optional[str] = None
    
    def _to_message(self):
        """
        Converts the message node to a dictionary representation suitable for messaging purposes.

        The method serializes the content attribute to a JSON string if it is a dictionary.
        Otherwise, it keeps the content as is.

        Returns:
            A dictionary representing the message with 'role' and 'content' keys.
        """
        out = {
            "role": self.role,
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content
            }
        return out

    def _create_role_message(self, role_: str, 
                             content: Any, 
                             content_key: str, 
                             name: Optional[str] = None
                             ) -> None:
        """
        Creates a message with a specific role, content, and an optional name.

        This method sets up the message node with the specified role, content, and name. The content
        is stored in a dictionary under the provided content_key.

        Args:
            role_ (str): The role of the message.
            content (Any): The content of the message.
            content_key (str): The key under which the content will be stored.
            name (Optional[str]): The name associated with the message. Defaults to the role if not provided.
        """
        self.role = role_
        self.content = {content_key: content}
        self.name = name or role_
        