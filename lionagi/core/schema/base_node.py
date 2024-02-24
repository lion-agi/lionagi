from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Callable
import pandas as pd

from ..util.sys_util import SysUtil
from ..util import create_id

import json
import xml.etree.ElementTree as ET

from pydantic import BaseModel, Field, AliasChoices

T = TypeVar('T', bound='BaseNode')


class BaseNode(BaseModel):
    """
    Represents a node with general information and metadata.

    This base class is designed to encapsulate a node's attributes, including
    identifiers, metadata, labels, related nodes, and content. It provides methods
    for serialization to and from various formats (e.g., JSON, XML), managing
    metadata, and relationship between nodes.

    Attributes: id_ (str): Unique identifier for the node, automatically generated. metadata (Dict[str,
    Any]): Key-value pairs for additional information about the node. label (Optional[str]): An optional descriptive
    label for the node. related_nodes (List[str]): Identifiers for nodes related to this node. content (Union[str,
    Dict[str, Any], None, Any]): Main content of the node, which can be text, structured data, or any serializable
    format.

    Examples:
        Creating a node with custom content:
        >>> node = BaseNode(content="Example content")
        Serializing a node to JSON:
        >>> json_str = node.to_json()
        Deserializing a node from JSON:
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

    # ------ constructor methods ------
    # noinspection PyShadowingNames
    @classmethod
    def from_pd_series(cls: Type[T], pd_series: pd.Series) -> T:
        """Creates an instance from a pandas Series.

        Args:
            pd_series (Series): A pandas Series object where index values correspond to attribute names.

        Returns:
            BaseNode: An instance populated with data from the pandas Series.

        Examples:
            >>> import pandas as pd
            >>> series = pd.Series({'content': 'Series content', 'label': 'Series Label'})
            >>> node = BaseNode.from_pd_series(series)
        """
        dict_ = pd_series.to_dict()
        return cls(**dict_)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Creates an instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing the node's data.

        Returns:
            BaseNode: A new instance populated with the specified data.

        Examples:
            >>> data_ = {'content': 'Example content', 'label': 'Example Label'}
            >>> node = BaseNode.from_dict(data_)
        """
        return cls(**data)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        """
        Creates an instance from a JSON string.

        Args:
            json_str (str): JSON string representation of the node's data.
            **kwargs: Additional keyword arguments passed to json.loads().

        Returns:
            BaseNode: A new instance populated with data parsed from the JSON string.

        Raises:
            ValueError: If the JSON string is invalid.

        Examples:
            >>> json_str_ = '{"content": "Example content", "label": "Example Label"}'
            >>> node = BaseNode.from_json(json_str_)
        """

        try:
            data = json.loads(json_str, **kwargs)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string provided for deserialization.") from e

    @classmethod
    def from_xml(cls: Type[T], xml_str: str) -> T:
        """
        Creates an instance from an XML string.

        Parses an XML string to extract node data, converting it into a dictionary
        before initializing a `BaseNode` instance.

        Args:
            xml_str (str): XML string representation of the node's data.

        Returns:
            BaseNode: A new instance populated with data parsed from the XML string.

        Examples:
            >>> xml_str_ = '<BaseNode><content>XML content</content><label>XML Label</label></BaseNode>'
            >>> node = BaseNode.from_xml(xml_str_)
        """
        root = ET.fromstring(xml_str)
        data = cls._xml_to_dict(root)
        return cls(**data)

    # ------ conversion methods ------

    def to_json(self) -> str:
        """
        Serializes the node instance to a JSON string.

        Converts the node's attributes into a JSON-formatted string, using attribute
        names as keys. This method is useful for exporting the node's state for storage
        or transmission over a network.

        Returns:
            str: JSON string representing the node.

        Examples:
            >>> node = BaseNode(content="Example content")
            >>> json_str = node.to_json()
            >>> print(json_str)
        """
        return self.model_dump_json(by_alias=True)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the node instance to a dictionary.

        Converts the node's attributes into a dictionary, with attribute names as keys.
        This method facilitates interoperability with other Python code that operates
        on standard data structures.

        Returns:
            Dict[str, Any]: A dictionary representation of the node.

        Examples:
            >>> node = BaseNode(content="Example content")
            >>> node_dict = node.to_dict()
            >>> print(node_dict)
        """
        return self.model_dump(by_alias=True)

    def to_xml(self) -> str:
        """
        Serializes the node instance to an XML string.

        Converts the node's attributes into an XML-formatted string. This method can
        be particularly useful when integrating with systems that require XML for data
        interchange.

        Returns:
            str: XML string representing the node.

        Examples:
            >>> node = BaseNode(content="Example content")
            >>> xml_str = node.to_xml()
            >>> print(xml_str)
        """
        root = ET.Element(self.__class__.__name__)
        for attr, value in self.to_dict().items():
            child = ET.SubElement(root, attr)
            child.text = str(value)
        return ET.tostring(root, encoding='unicode')

    def to_pd_series(self) -> pd.Series:
        """
        Converts the node instance to a pandas Series object.

        This method facilitates the use of node data within the pandas ecosystem, allowing
        for easy integration with data analysis and manipulation workflows.

        Returns:
            Series: A pandas Series object representing the node, with attribute names as index labels.

        Examples:
            >>> node = BaseNode(content="Example content")
            >>> series = node.to_pd_series()
            >>> print(series)
        """
        return pd.Series(self.to_dict())

    def clone(self):
        cls = self.__class__
        return cls(**self.to_dict())

    # ------ meta methods -----
    @property
    def metadata_keys(self) -> List[str]:
        """
        Retrieves a list of all metadata keys present in the node.

        This method provides a convenient way to inspect the keys available in the
        node's metadata, facilitating easier exploration and manipulation of metadata.

        Returns:
            List[str]: A list of metadata keys.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe", "year": 2020})
            >>> print(node.meta_keys)
            ['author', 'year']
        """
        return list(self.metadata.keys())

    def has_metadata_key(self, key: str) -> bool:
        """
        Determines if a specified key exists in the node's metadata.

        This method checks whether the given key is present in the node's metadata,
        facilitating conditional checks and dynamic metadata manipulation.

        Args:
            key (str): The metadata key to check for existence.

        Returns:
            bool: True if the key exists in the metadata, False otherwise.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> print(node.has_meta_key("author"))
            True
            >>> print(node.has_meta_key("publisher"))
            False
        """
        return key in self.metadata

    def get_metadata(self, key: str, default=None) -> Any:
        """
        Retrieves the value associated with a specified metadata key.

        This method provides a way to access values in the node's metadata, with an
        option to specify a default value if the key is not found.

        Args:
            key (str): The metadata key for which to retrieve the value.
            default (Optional[Any]): The default value to return if the key is not found. Defaults to None.

        Returns:
            Any: The value associated with the specified key, or the default value if the key is not found.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> print(node.get_metadata("author"))
            John Doe
            >>> print(node.get_meta_key("publisher", default="Unknown"))
            Unknown
        """
        return self.metadata.get(key, default)

    def change_metadata_key(self, old_key: str, new_key: str) -> bool:
        """
        Renames a key in the node's metadata.

        This method allows for the renaming of a metadata key, preserving the associated
        value under the new key name. This can be useful for updating or standardizing
        metadata keys.

        Args:
            old_key (str): The current name of the metadata key.
            new_key (str): The new name for the metadata key.

        Returns:
            bool: True if the key was successfully renamed, False otherwise (e.g., if the old key does not exist).

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> success = node.change_metadata_key("author", "creator")
            >>> print(success)
            True
            >>> print(node.metadata)
            {'creator': 'John Doe'}
        """
        if old_key in self.metadata:
            SysUtil.change_dict_key(self.metadata, old_key=old_key, new_key=new_key)
            return True
        return False

    def pop_metadata(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Deletes a specified key from the node's metadata and returns its value.

        This method removes a key-value pair from the node's metadata and returns the value
        associated with the key. If the key does not exist, it returns a default value if provided,
        mirroring the behavior of the `dict.pop` method.

        Args:
            key (str): The metadata key to delete and retrieve its value.
            default (Optional[Any]): The default value to return if the key does not exist. Defaults to None.

        Returns:
            Any: The value of the deleted metadata entry if the key exists, otherwise the default value.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe", "year": 2020})
            >>> author = node.pop_metadata("author")
            >>> print(author)
            John Doe
            >>> year = node.pop_metadata("year", default="Not Specified")
            >>> print(year)
            2020
            >>> genre = node.pop_metadata("genre", default="Not Specified")
            >>> print(genre)
            Not Specified
        """
        return self.metadata.pop(key, default)

    def merge_metadata(self, additional_metadata: Dict[str, Any], overwrite: bool = False) -> None:
        """
        Merges another metadata dictionary into the node's existing metadata.

        This method combines metadata from another dictionary with the node's current
        metadata. By default, existing keys will not be overwritten unless explicitly
        specified.

        Args: additional_metadata (Dict[str, Any]): The metadata dictionary to merge with the node's metadata.
        overwrite (bool): Determines whether existing keys should be overwritten by those in `other_metadata`.
        Defaults to False.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> additional_metadata_ = {"year": 2020, "publisher": "Fiction Press"}
            >>> node.merge_metadata(additional_metadata_, overwrite=True)
            >>> print(node.metadata)
            {'author': 'John Doe', 'year': 2020, 'publisher': 'Fiction Press'}
        """
        if not overwrite:
            additional_metadata = ({
                k: v for k, v in additional_metadata.items()
                if k not in self.metadata
            })
        self.metadata.update(additional_metadata)

    def clear_metadata(self) -> None:
        """
        Clears all entries in the node's metadata.

        This method removes all key-value pairs from the node's metadata, effectively
        resetting it to an empty state. This is useful for cases where you need to
        start fresh with the node's metadata without creating a new node instance.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe", "year": 2020})
            >>> print(node.metadata)
            {'author': 'John Doe', 'year': 2020}
            >>> node.clear_metadata()
            >>> print(node.metadata)
            {}
        """

        self.metadata.clear()

    def filter_metadata(self, filter_func: Callable[[Any], bool]) -> Dict[str, Any]:
        """
        Filters the node's metadata based on a provided filter function.

        Applies a filter function to each metadata entry (key-value pair) and returns
        a new dictionary containing only the entries for which the filter function returns True.

        Args:
            filter_func (Callable[[Any], bool]): A function that takes a metadata value as input_
                and returns True if the entry should be included in the filtered result.

        Returns:
            Dict[str, Any]: A dictionary containing the filtered metadata entries.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe", "year": 2020, "genre": "Fiction"})
            >>> filtered_metadata = node.filter_metadata(lambda value: isinstance(value, str))
            >>> print(filtered_metadata)
            {'author': 'John Doe', 'genre': 'Fiction'}
        """
        return {k: v for k, v in self.metadata.items() if filter_func(v)}

    def validate_metadata(self, schema: Dict[str, Type]) -> bool:
        """
        Validates the node's metadata against a specified schema.

        This method checks if the node's metadata conforms to a given schema, where
        the schema is defined as a dictionary with metadata keys and their expected
        types. It returns True if the metadata matches the schema, otherwise False.

        Args:
            schema (Dict[str, Type]): A dictionary defining the expected types for each metadata key.

        Returns:
            bool: True if the metadata conforms to the schema, False otherwise.

        Examples:
            >>> schema_ = {"author": str, "year": int, "genre": str}
            >>> node = BaseNode(metadata={"author": "John Doe", "year": "2020"})
            >>> is_valid = node.validate_metadata(schema_)
            >>> print(is_valid)
            False
        """

        return SysUtil.is_schema(dict_=self.metadata, schema=schema)

    # ----- nodes relationship -----

    def add_related_node(self, node_id: str) -> bool:
        """
        Adds a related node ID to the list of related nodes.

        This method appends a new node ID to the node's list of related nodes if it is
        not already present. It ensures that each related node ID is unique within the list.

        Args:
            node_id (str): The ID of the node to add as related.

        Returns:
            bool: True if the node ID was added, False if it was already present.

        Examples:
            >>> node = BaseNode()
            >>> added = node.add_related_node("12345")
            >>> print(added)
            True
            >>> added_again = node.add_related_node("12345")
            >>> print(added_again)
            False
        """
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)
            return True
        return False

    def remove_related_node(self, node_id: str) -> bool:
        """
        Removes a related node ID from the list of related nodes.

        This method removes an existing node ID from the node's list of related nodes,
        if it exists. It facilitates managing dynamic relationship between nodes.

        Args:
            node_id (str): The ID of the node to remove from related nodes.

        Returns:
            bool: True if the node ID was removed, False if it was not found.

        Examples:
            >>> node = BaseNode(related_nodes=["12345", "67890"])
            >>> removed = node.remove_related_node("12345")
            >>> print(removed)
            True
            >>> removed_again = node.remove_related_node("12345")
            >>> print(removed_again)
            False
        """
        if node_id in self.related_nodes:
            self.related_nodes.remove(node_id)
            return True
        return False

    # ------ utility ------
    def validate_content(self, schema: Dict[str, type]) -> bool:
        """
        Validates the node's content against a specified schema.

        This method checks if the structured content of the node conforms to a given
        schema. The schema is defined as a dictionary mapping content keys to their
        expected types. It returns True if the content matches the schema, otherwise False.

        Args:
            schema (Dict[str, Type]): A dictionary defining the expected types for each content key.

        Returns:
            bool: True if the content conforms to the schema, False otherwise.

        Examples:
            >>> node = BaseNode(content={"category": "New Beginnings", "year": 2021})
            >>> schema_ = {"category": str, "year": int}
            >>> is_valid = node.validate_content(schema_)
            >>> print(is_valid)
            True
        """
        if not isinstance(self.content, Dict):
            return False
        return SysUtil.is_schema(self.content, schema)

    def __str__(self) -> str:
        """
        Provides a string representation of the BaseNode instance for easy reading.

        This method returns a string that summarizes the key attributes of the node,
        including its ID, label, content preview, metadata, and related nodes. It's
        designed for readability rather than completeness.

        Returns:
            str: A human-readable string representation of the node.

        Examples:
            >>> node = BaseNode(id_="001", label="Example Node", content="This is an example.")
            >>> print(str(node))
            BaseNode(id=001, label=Example Node, content='This is an examp...', metadata='{}', related_nodes=[])
        """
        content_preview = (str(self.content)[:75] + '...') if len(str(self.content)) > 75 else str(self.content)
        metadata_preview = str(self.metadata)[:75] + '...' if len(str(self.metadata)) > 75 else str(self.metadata)
        related_nodes_preview = ', '.join(self.related_nodes[:3]) + ('...' if len(self.related_nodes) > 3 else '')
        return (f"{self.__class__.__name__}(id={self.id_}, label={self.label}, "
                f"content='{content_preview}', metadata='{metadata_preview}', "
                f"related_nodes=[{related_nodes_preview}])")

    def __repr__(self):
        """
        Provides a machine-readable representation of the BaseNode instance.

        This method returns a string that accurately represents how to reconstruct
        the node instance programmatically. It's primarily intended for debugging
        and development purposes.

        Returns:
            str: A machine-readable string representation of the node.

        Examples:
            >>> node = BaseNode(id_="001", label="Example Node", content="This is an example.")
            >>> print(repr(node))
            BaseNode(id_='001', label='Example Node', content='This is an example.', metadata={}, related_nodes=[])
        """
        return f"{self.__class__.__name__}({self.to_json()})"
