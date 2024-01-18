import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, TypeVar, Type, List, Callable, Union
from pydantic import BaseModel, Field, AliasChoices

from ..utils.sys_util import create_id, change_dict_key, is_schema
from ..utils.encrypt_util import EncrytionUtil

T = TypeVar('T', bound='BaseNode')


class BaseNode(BaseModel):
    """
    The base class for nodes containing general information and metadata.

    Attributes:
        id_ (str): The unique identifier for the node.
        metadata (Dict[str, Any]): Additional metadata for the node.
        label (Optional[str]): An optional label for the node.
        related_nodes (List[str]): List of related node IDs.
        content (Union[str, Dict[str, Any], None, Any]): The content of the node.

    Examples:
        >>> node = BaseNode(content="Example content")
        >>> node_dict = node.to_dict()
        >>> json_str = node.to_json()
        >>> same_node = BaseNode.from_json(json_str)
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
        validate_return = True
        str_strip_whitespace = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> T:
        """
        Creates an instance of the class from a dictionary.

        Args:
            data: A dictionary containing the node's data.

        Returns:
            An instance of the class.

        Examples:
            >>> data = {"content": "Example content"}
            >>> node = BaseNode.from_dict(data)
        """
        return cls(**data)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        """
        Creates an instance of the class from a JSON string.

        Args:
            json_str: A JSON string containing the node's data.
            **kwargs: Additional keyword arguments to pass to json.loads.

        Returns:
            An instance of the class.

        Examples:
            >>> json_str = '{"content": "Example content"}'
            >>> node = BaseNode.from_json(json_str)
        """
        try:
            data = json.loads(json_str, **kwargs)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string provided for deserialization.") from e

    @classmethod
    def from_xml(cls, xml_str: str) -> T:
        """
        Creates an instance of the class from an XML string.

        Args:
            xml_str: An XML string containing the node's data.

        Returns:
            An instance of the class.

        Examples:
            >>> xml_str = "<BaseNode><content>Example content</content></BaseNode>"
            >>> node = BaseNode.from_xml(xml_str)
        """
        root = ET.fromstring(xml_str)
        data = cls._xml_to_dict(root)
        return cls(**data)

    def to_json(self) -> str:
        """
        Converts the instance to a JSON string.

        Returns:
            A JSON string representing the node.

        Examples:
            >>> node = BaseNode(content="Example content")
            >>> json_str = node.to_json()
        """
        return self.model_dump_json(by_alias=True)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the instance to a dictionary.

        Returns:
            A dictionary representing the node.

        Examples:
            >>> node = BaseNode(content="Example content")
            >>> node_dict = node.to_dict()
        """
        return self.model_dump(by_alias=True)

    def to_xml(self) -> str:
        """
        Converts the instance to an XML string.

        Returns:
            An XML string representing the node.

        Examples:
            >>> node = BaseNode(content="Example content")
            >>> xml_str = node.to_xml()
        """
        root = ET.Element(self.__class__.__name__)
        for attr, value in self.to_dict().items():
            child = ET.SubElement(root, attr)
            child.text = str(value)
        return ET.tostring(root, encoding='unicode')

    def validate_content(self, schema: Dict[str, type]) -> bool:
        """
        Validates the node's content against a schema.

        Args:
            schema: The schema to validate against.

        Returns:
            True if the content matches the schema, False otherwise.

        Examples:
            >>> schema = {"title": str, "body": str}
            >>> node = BaseNode(content={"title": "Example", "body": "Content"})
            >>> node.validate_content(schema)
        """
        if not isinstance(self.content, dict):
            return False
        return is_schema(self.content, schema)

    @property
    def meta_keys(self) -> List[str]:
        """
        List of metadata keys.

        Returns:
            A list of keys in the metadata dictionary.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.meta_keys
        """
        return list(self.metadata.keys())

    def has_meta_key(self, key: str) -> bool:
        """
        Checks if a metadata key exists.

        Args:
            key: The metadata key to check for.

        Returns:
            True if the key exists, False otherwise.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.has_meta_key("author")
        """
        return key in self.metadata

    def get_meta_key(self, key: str) -> Any:
        """
        Retrieves a value from the metadata dictionary.

        Args:
            key: The key for the value to retrieve.

        Returns:
            The value associated with the key, if it exists.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.get_meta_key("author")
        """
        return self.metadata.get(key)

    def change_meta_key(self, old_key: str, new_key: str) -> bool:
        """
        Changes a key in the metadata dictionary.

        Args:
            old_key: The old key name.
            new_key: The new key name.

        Returns:
            True if the key was changed successfully, False otherwise.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.change_meta_key("author", "creator")
        """
        if old_key in self.metadata:
            change_dict_key(self.metadata, old_key=old_key, new_key=new_key)
            return True
        return False

    def delete_meta_key(self, key: str) -> bool:
        """
        Deletes a key from the metadata dictionary.

        Args:
            key: The key to delete.

        Returns:
            True if the key was deleted, False otherwise.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.delete_meta_key("author")
        """
        if key in self.metadata:
            del self.metadata[key]
            return True
        return False
            
    def merge_meta(self, other_metadata: Dict[str, Any], overwrite: bool = False) -> None:
        """
        Merges another metadata dictionary into the current metadata.

        Args:
            other_metadata: The metadata dictionary to merge.
            overwrite: If True, existing keys will be overwritten.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> new_meta = {"editor": "Jane Smith"}
            >>> node.merge_meta(new_meta)
        """
        if not overwrite:
            other_metadata = ({
                k: v for k, v in other_metadata.items() 
                if k not in self.metadata
            })
        self.metadata.update(other_metadata)

    def clear_meta(self) -> None:
        """
        Clears the metadata dictionary.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.clear_meta()
        """

        self.metadata.clear()

    def filter_meta(self, filter_func: Callable[[Any], bool]) -> Dict[str, Any]:
        """
        Filters the metadata dictionary based on a filter function.

        Args:
            filter_func: The function to filter metadata items.

        Returns:
            A dictionary containing the filtered metadata items.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe", "year": 2020})
            >>> filtered_meta = node.filter_meta(lambda x: isinstance(x, str))
        """
        return {k: v for k, v in self.metadata.items() if filter_func(v)}

    def validate_meta(self, schema: Dict[str, type]) -> bool:
        """
        Validates the metadata against a schema.

        Args:
            schema: The schema to validate against.

        Returns:
            True if the metadata matches the schema, False otherwise.

        Examples:
            >>> schema = {"author": str, "year": int}
            >>> node = BaseNode(metadata={"author": "John Doe", "year": 2020})
            >>> node.validate_meta(schema)
        """
        return is_schema(dict_=self.metadata, schema=schema)

    def encrypt_content(self, key: str) -> None:
        """
        Encrypts the node's content.

        Args:
            key: The encryption key.

        Examples:
            >>> node = BaseNode(content="Sensitive information")
            >>> node.encrypt_content("my_secret_key")
        """
        self.content = EncrytionUtil.encrypt(self.content, key)

    def decrypt_content(self, key: str) -> None:
        """
        Decrypts the node's content.

        Args:
            key: The decryption key.

        Examples:
            >>> node = BaseNode(content="Encrypted content")
            >>> node.decrypt_content("my_secret_key")
        """
        self.content = EncrytionUtil.decrypt(self.content, key)

    def add_related_node(self, node_id: str) -> bool:
        """
        Adds a related node ID to the list of related nodes.

        Args:
            node_id: The ID of the related node to add.

        Returns:
            True if the ID was added, False if it was already in the list.

        Examples:
            >>> node = BaseNode()
            >>> related_node_id = "123456"
            >>> node.add_related_node(related_node_id)
        """
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)
            return True
        return False

    def remove_related_node(self, node_id: str) -> bool:
        """
        Removes a related node ID from the list of related nodes.

        Args:
            node_id: The ID of the related node to remove.

        Returns:
            True if the ID was removed, False if it was not in the list.

        Examples:
            >>> node = BaseNode(related_nodes=["123456"])
            >>> related_node_id = "123456"
            >>> node.remove_related_node(related_node_id)
        """
        if node_id in self.related_nodes:
            self.related_nodes.remove(node_id)
            return True
        return False

    def __str__(self) -> str:
        """String representation of the BaseNode instance."""
        content_preview = (str(self.content)[:75] + '...') if len(str(self.content)) > 75 else str(self.content)
        metadata_preview = str(self.metadata)[:75] + '...' if len(str(self.metadata)) > 75 else str(self.metadata)
        related_nodes_preview = ', '.join(self.related_nodes[:3]) + ('...' if len(self.related_nodes) > 3 else '')
        return (f"{self.__class__.__name__}(id={self.id_}, label={self.label}, "
                f"content='{content_preview}', metadata='{metadata_preview}', "
                f"related_nodes=[{related_nodes_preview}])")

    def __repr__(self):
        """Machine-readable representation of the BaseNode instance."""
        return f"{self.__class__.__name__}({self.to_json()})"

    @staticmethod
    def _xml_to_dict(root: ET.Element) -> Dict[str, Any]:
        data = {}
        for child in root:
            data[child.tag] = child.text
        return data


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
