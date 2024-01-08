import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, TypeVar, Type, List, Callable, Union
from pydantic import BaseModel, Field, AliasChoices

from ..utils.sys_util import create_id

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

    # ----------------- construct nodes from [json, dict, xml] ----------------------
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


    # --------------------- convert nodes to [json, dict, xml] -----------------------
    def to_json(self) -> str:
        """Converts the node instance into JSON string representation."""
        return self.model_dump_json(by_alias=True)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the node instance into a dictionary representation."""
        return self.model_dump(by_alias=True)
    
    def to_xml(self) -> str:
        """Converts the node instance into XML string representation."""
        return self._dict_to_xml(self.to_dict())


    # -------------------------- metadata manipulation -----------------------------------
    def set_meta(self, metadata_: Dict[str, Any]) -> None:
        self.metadata = metadata_
        
    def get_meta_key(self, key: str) -> Any:
        """Retrieves a value from the metadata by key."""
        return self.metadata.get(key)

    def update_meta_key(self, key: str, value: Any) -> None:
        """Updates or adds a key-value pair in the metadata."""
        self.metadata[key] = value

    def delete_meta_key(self, key: str) -> None:
        """Deletes a key from the metadata."""
        if key in self.metadata:
            del self.metadata[key]

    def merge_metadata(self, other_metadata: Dict[str, Any], overwrite: bool = True) -> None:
        """Merges another dictionary into the node's metadata."""
        if not overwrite:
            other_metadata = {k: v for k, v in other_metadata.items() if k not in self.metadata}
        self.metadata.update(other_metadata)

    def clear_metadata(self) -> None:
        """Clears all metadata from the node."""
        self.metadata.clear()

    @property
    def metadata_keys(self) -> List[str]:
        """Returns a list of all keys currently in the metadata."""
        return list(self.metadata.keys())

    def has_metadata_key(self, key: str) -> bool:
        """Checks if a certain key exists in the metadata."""
        return key in self.metadata

    def filter_metadata(self, filter_func: Callable[[Any], bool]) -> Dict[str, Any]:
        """Filters the metadata based on a provided function or criteria."""
        return {k: v for k, v in self.metadata.items() if filter_func(v)}

    def apply_to_metadata(self, apply_func: Callable[[Any], Any]) -> None:
        """Applies a function to the metadata or to specific items within the metadata."""
        for key in self.metadata:
            self.metadata[key] = apply_func(self.metadata[key])
        
        
    # ----------------------------------- Data Validation --------------------------------

    def validate_metadata_structure(self, schema: Dict[str, type]) -> bool:
        """
        Validates the metadata structure against a given schema.

        Parameters:
            schema (Dict[str, type]): A dictionary representing the expected schema 
                                    with key-value pairs where values are types.

        Returns:
            bool: True if metadata matches the schema, False otherwise.
        """
        for key, expected_type in schema.items():
            if not isinstance(self.metadata.get(key), expected_type):
                return False
        return True



















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



    def _dict_to_xml(data: Dict[str, Any], root_tag: str = 'node') -> str:
        """
        Helper method to convert a dictionary to an XML string.

        Parameters:
            data (Dict[str, Any]): The dictionary to convert to XML.
            root_tag (str): The root tag name for the XML.

        Returns:
            str: An XML string representation of the dictionary.
        """
        root = ET.Element(root_tag)
        BaseNode._build_xml(root, data)
        return ET.tostring(root, encoding='unicode')
    
    @staticmethod
    def _build_xml(element: ET.Element, data: Any):
        """Recursively builds XML elements from data."""
        if isinstance(data, dict):
            for key, value in data.items():
                sub_element = ET.SubElement(element, key)
                BaseNode._build_xml(sub_element, value)
        elif isinstance(data, list):
            for item in data:
                item_element = ET.SubElement(element, 'item')
                BaseNode._build_xml(item_element, item)
        else:
            element.text = str(data)







    # def __eq__(self, other: object) -> bool:
    #     if not isinstance(other, T):
    #         return NotImplemented
    #     return self.model_dump() == other.model_dump()

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

    


