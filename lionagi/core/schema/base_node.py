"""
Module for base component model definition using Pydantic.
"""

from abc import ABC
from functools import singledispatchmethod

from typing import Any, Type, TypeVar, Callable

import lionagi.integrations.bridge.pydantic_.base_model as pyd

from lionagi.libs.sys_util import SysUtil
from lionagi.libs import ln_dataframe as dataframe
from lionagi.libs import ln_convert as convert
from lionagi.libs import ln_nested as nested


T = TypeVar("T", bound="BaseComponent")


class BaseComponent(pyd.ln_BaseModel, ABC):
    """
    A base component model that provides common attributes and utility methods for metadata management.
    It includes functionality to interact with metadata in various ways, such as retrieving, modifying,
    and validating metadata keys and values.

    Attributes:
        id_ (str): Unique identifier, defaulted using SysUtil.create_id.
        timestamp (str | None): Timestamp of creation or modification.
        metadata (dict[str, Any]): Metadata associated with the component.
    """

    id_: str = pyd.ln_Field(default_factory=SysUtil.create_id, alias="node_id")
    timestamp: str | None = pyd.ln_Field(default_factory=SysUtil.get_timestamp)
    metadata: dict[str, Any] = pyd.ln_Field(default_factory=dict, alias="meta")

    class Config:
        """Model configuration settings."""

        extra = "allow"
        populate_by_name = True
        validate_assignment = True
        validate_return = True
        str_strip_whitespace = True

    @classmethod
    def class_name(cls) -> str:
        """
        Returns the class name of the model.
        """
        return cls.__name__

    # from_obj method, overloaded
    # implemented for dict, str, pd.Series, pd.DataFrame, list, pydantic.BaseModel

    @singledispatchmethod
    @classmethod
    def from_obj(cls: Type[T], obj: Any, *args, **kwargs) -> T:
        """
        Generic method to create an instance of the class from an object. This method should be
        overridden by registering handlers for specific types.

        Args:
            obj (Any): The input object from which to create an instance of the class.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Raises:
            NotImplementedError: If no handler is registered for the type of `obj`.

        Returns:
            T: An instance of the class.
        """
        raise NotImplementedError(f"Unsupported type: {type(obj)}")

    @from_obj.register
    @classmethod
    def _(cls, dict_data: dict, *args, **kwargs) -> T:
        """
        Handles creation of an instance from a dictionary object.

        Args:
            dict_data (dict): The dictionary from which to create an instance of the class.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            T: An instance of the class created from the dictionary.
        """
        return cls.model_validate(dict_data, *args, **kwargs)

    @from_obj.register(str)
    @classmethod
    def _(cls, json_data: str, *args, **kwargs) -> T:
        """
        Overloaded method to handle JSON string inputs.

        Args:
            json_data (str): The JSON string to convert to an instance of the class.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments for JSON deserialization.

        Returns:
            T: An instance of the class created from the JSON string.

        Raises:
            ValueError: If the JSON string is invalid.
        """
        try:
            return cls.from_obj(convert.to_dict(json_data), *args, **kwargs)
        except pyd.ln_ValidationError as e:
            raise ValueError(f"Invalid JSON for deserialization: {e}")

    @from_obj.register(dataframe.ln_Series)
    @classmethod
    def _(cls, pd_series, *args, pd_kwargs: dict | None = None, **kwargs) -> T:
        """
        Handles creation of an instance from a pandas Series object.

        Args:
            pd_series (pd.Series): The pandas Series from which to create an instance of the class.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            T: An instance of the class created from the pandas Series.
        """
        pd_kwargs = pd_kwargs or {}
        pd_dict = convert.to_dict(pd_series, **pd_kwargs)
        return cls.from_obj(pd_dict, *args, **kwargs)

    @from_obj.register(dataframe.ln_DataFrame)
    @classmethod
    def _(cls, pd_df, *args, pd_kwargs: dict | None = None, **kwargs) -> list[T]:
        """
        Handles creation of instances from a pandas DataFrame object, returning a list of instances.

        Args:
            pd_df (pd.DataFrame): The pandas DataFrame from which to create instances of the class.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            list[T]: A list of instances of the class created from each row of the pandas DataFrame.
        """
        pd_kwargs = pd_kwargs or {}
        pd_dict = convert.to_dict(pd_df, as_list=True, **pd_kwargs)
        return cls.from_obj(pd_dict, *args, **kwargs)

    @from_obj.register(list)
    @classmethod
    def _(cls, list_data: list[Any], *args, **kwargs) -> list[T]:
        """
        Overloaded method to handle list inputs, converting each element in the list to an instance of the class.

        Args:
            list_data (list[Any]): The list to convert to instances of the class.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments for list element conversion.

        Returns:
            list[T]: A list of instances of the class created from each element of the input list.
        """
        return [cls.from_obj(item, *args, **kwargs) for item in list_data]

    @from_obj.register(pyd.ln_BaseModel)
    @classmethod
    def _(cls, model, *args, model_kwargs=None, **kwargs) -> T:
        model_kwargs = model_kwargs or {}
        model_dict = {}
        try:
            model_dict = model.model_dump(by_alias=True, **model_kwargs)
        except:
            model_dict = model.to_dict(**model_kwargs)
        return cls.model_validate(model_dict, *args, **kwargs)

    # to obj methods, not overloaded

    def to_json_data(self, *args, **kwargs) -> str:
        """
        Serializes the instance to a JSON string.

        Args:
            *args: Variable length argument list for additional options.
            **kwargs: Arbitrary keyword arguments for Pydantic's json() method.

        Returns:
            str: The JSON string representation of the instance.
        """
        return self.model_dump_json(*args, by_alias=True, **kwargs)

    def to_dict(self, *args, **kwargs) -> dict[str, Any]:
        """
        Serializes the instance to a dictionary.

        Args:
            *args: Variable length argument list for additional options.
            **kwargs: Arbitrary keyword arguments for Pydantic's dict() method.

        Returns:
            dict[str, Any]: The dictionary representation of the instance.
        """
        return self.model_dump(*args, by_alias=True, **kwargs)

    def to_xml(self) -> str:
        """
        Serializes the instance to an XML string. This method assumes a simple conversion
        process suitable for basic instances. For complex cases, customization may be required.

        Returns:
            str: The XML string representation of the instance.
        """
        import xml.etree.ElementTree as ET

        root = ET.Element(self.__class__.__name__)

        def convert(dict_obj, parent):
            for key, val in dict_obj.items():
                if isinstance(val, dict):
                    element = ET.SubElement(parent, key)
                    convert(val, element)
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(val)

        convert(self.to_dict(), root)
        return ET.tostring(root, encoding="unicode")

    def to_pd_series(
        self, *args, pd_kwargs: dict | None = None, **kwargs
    ) -> dataframe.ln_Series:
        """
        Converts the instance to a pandas Series.

        Args:
            *args: Arguments for self.to_dict method.
            pd_kwargs: Keyword arguments for pd.Series constructor.
            **kwargs: Keyword arguments for self.to_dict method.

        Returns:
            pd.Series: The instance represented as a pandas Series.
        """
        pd_kwargs = {} if pd_kwargs is None else pd_kwargs
        dict_ = self.to_dict(*args, **kwargs)
        return dataframe.ln_Series(dict_, **pd_kwargs)

    def copy(self, *args, **kwargs) -> T:
        """
        Creates a deep copy of the instance, with an option to update specific fields.

        Args:
            *args: Variable length argument list for additional options.
            **kwargs: Arbitrary keyword arguments specifying updates to the instance.

        Returns:
            BaseComponent: A new instance of BaseComponent as a deep copy of the original, with updates applied.
        """
        return self.model_copy(*args, **kwargs)

    # meta methods

    def meta_keys(self, flattened: bool = False, **kwargs) -> list[str]:
        """
        lists the keys in the metadata dictionary. Optionally returns flattened keys for nested structures.

        Args:
            flattened (bool): If True, returns the keys in a flattened format for nested dictionaries.
            **kwargs: Additional keyword arguments passed to get_flattened_keys function when flattened is True.

        Returns:
            list[str]: A list of keys from the metadata dictionary.
        """
        if flattened:
            return nested.get_flattened_keys(self.metadata, **kwargs)
        return list(self.metadata.keys())

    def meta_has_key(self, key: str, flattened: bool = False, **kwargs) -> bool:
        """
        Checks if a specific key exists in the metadata dictionary.

        Args:
            key (str): The key to check in the metadata.
            flattened (bool): If True, checks for the key in a flattened metadata structure.
            **kwargs: Additional keyword arguments passed to get_flattened_keys function when flattened is True.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        if flattened:
            return key in nested.get_flattened_keys(self.metadata, **kwargs)
        return key in self.metadata

    def meta_get(self, key: str, indices=None, default: Any = None) -> Any:
        """Retrieves metadata value by key with default."""
        if indices:
            return nested.nget(self.metadata, key, indices, default)
        return self.metadata.get(key, default)

    def meta_change_key(self, old_key: str, new_key: str) -> bool:
        """Renames a key in metadata if it exists."""
        if old_key in self.metadata:
            SysUtil.change_dict_key(self.metadata, old_key, new_key)
            return True
        return False

    def meta_insert(self, indices: str | list, value: Any, **kwargs) -> bool:
        """Inserts a value into metadata at the specified key."""
        return nested.ninsert(self.metadata, indices, value, **kwargs)

    # ToDo: do a nested pop
    def meta_pop(self, key: str, default: Any = None) -> Any:
        """Pops a key from metadata, returning its value or default."""
        return self.metadata.pop(key, default)

    def meta_merge(
        self, additional_metadata: dict[str, Any], overwrite: bool = False, **kwargs
    ) -> None:
        """
        Merges another dictionary into metadata with optional overwrite.
        kwargs for nmerge
        """
        nested.nmerge(
            [self.metadata, additional_metadata], overwrite=overwrite, **kwargs
        )

        for key, value in additional_metadata.items():
            if overwrite or key not in self.metadata:
                self.metadata[key] = value

    def meta_clear(self) -> None:
        """
        Clears all keys and values from the metadata dictionary.
        """
        self.metadata.clear()

    def meta_filter(self, condition: Callable[[Any, Any], bool]) -> dict[str, Any]:
        """
        Filters the metadata dictionary based on a predicate function.

        Args:
            condition (Callable[[Any, Any], bool]): A function that takes a key-value pair and
            returns True if the pair should be included in the output.

        Returns:
            dict[str, Any]: A new dictionary containing only the key-value pairs that match the condition.
        """
        return nested.nfilter(self.metadata, condition)

    def meta_validate(self, schema: dict[str, Type | Callable]) -> bool:
        """
        Validates the metadata dictionary against a specified schema.

        Args:
            schema (dict[str, Union[Type[Any], Callable[[Any], bool]]]): A dictionary where each key is
            a metadata key to validate, and the value is the type expected or a function that takes
            the value and returns True if it's valid.

        Returns:
            bool: True if all specified metadata keys match their respective types or validation functions; False otherwise.
        """
        for key, validator in schema.items():
            value = self.metadata.get(key)
            if isinstance(validator, type):
                if not isinstance(value, validator):
                    return False
            elif Callable(validator):
                if not validator(value):
                    return False
        return True

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"

    # @classmethod
    # def from_xml(cls: Type[T], xml_str: str, **kwargs) -> T:
    #     """
    #     Creates an instance from an XML string.
    #     kwargs for pydantic model_validate method.
    #     """
    #     import xml.etree.ElementTree as ET
    #
    #     root = ET.fromstring(xml_str)
    #     data = cls._xml_to_dict(root)
    #     return cls.from_dict(data, **kwargs)

    # @staticmethod
    # def _xml_to_dict(root) -> dict[str, Any]:
    #     """Converts a flat XML structure to a dictionary."""
    #     return {child.tag: child.text for child in root}


class BaseNode(BaseComponent):
    """
    A base class for nodes, representing a fundamental unit in a graph or tree structure,
    extending BaseComponent with content handling capabilities.

    Attributes:
        content: The content of the node, which can be a string, a dictionary with any structure,
            None, or any other type. It is flexible to accommodate various types of content.
            This attribute also supports aliasing through validation_alias for compatibility with
            different naming conventions like "text", "page_content", or "chunk_content".
    """

    content: str | dict[str, Any] | None | Any = pyd.ln_Field(
        default=None,
        validation_alias=pyd.ln_AliasChoices("text", "page_content", "chunk_content"),
    )

    @property
    def content_str(self):
        """
        Attempts to serialize the node's content to a string.

        Returns:
            str: The serialized content string. If serialization fails, returns "null" and
                logs an error message indicating the content is not serializable.
        """
        try:
            return convert.to_str(self.content)
        except ValueError:
            print(
                f"Content is not serializable for Node: {self._id}, defaulting to 'null'"
            )
            return "null"

    def __str__(self):
        """
        Provides a string representation of the BaseNode instance, including a content preview,
        metadata preview, and optionally the timestamp if present.

        Returns:
            str: A string representation of the instance.
        """
        timestamp = f" ({self.timestamp})" if self.timestamp else ""
        if self.content:
            content_preview = (
                self.content[:50] + "..." if len(self.content) > 50 else self.content
            )
        else:
            content_preview = ""
        meta_preview = (
            str(self.metadata)[:50] + "..."
            if len(str(self.metadata)) > 50
            else str(self.metadata)
        )
        return (
            f"{self.class_name()}({self.id_}, {content_preview}, {meta_preview},"
            f"{timestamp})"
        )


class BaseRelatableNode(BaseNode):
    """
    Extends BaseNode with functionality to manage relationships with other nodes.

    Attributes:
        related_nodes: A list of identifiers (str) for nodes that are related to this node.
        label: An optional label for the node, providing additional context or classification.
    """

    related_nodes: list[str] = pyd.ln_Field(default_factory=list)
    label: str | None = None

    def add_related_node(self, node_id: str) -> bool:
        """
        Adds a node to the list of related nodes if it's not already present.

        Args:
            node_id: The identifier of the node to add.

        Returns:
            bool: True if the node was added, False if it was already in the list.
        """
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)
            return True
        return False

    def remove_related_node(self, node_id: str) -> bool:
        """
        Removes a node from the list of related nodes if it's present.

        Args:
            node_id: The identifier of the node to remove.

        Returns:
            bool: True if the node was removed, False if it was not found in the list.
        """

        if node_id in self.related_nodes:
            self.related_nodes.remove(node_id)
            return True
        return False


class Tool(BaseRelatableNode):
    """
    Represents a tool, extending BaseRelatableNode with specific functionalities and configurations.

    Attributes:
        func: The main function or capability of the tool.
        schema_: An optional schema defining the structure and constraints of data the tool works with.
        manual: Optional documentation or manual for using the tool.
        parser: An optional parser associated with the tool for data processing or interpretation.
    """

    func: Any
    schema_: dict | None = None
    manual: Any | None = None
    parser: Any | None = None

    @pyd.ln_field_serializer("func")
    def serialize_func(self, func):
        return func.__name__


TOOL_TYPE = bool | Tool | str | list[Tool | str | dict] | dict
