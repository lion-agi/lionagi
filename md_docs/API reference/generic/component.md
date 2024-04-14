
## BaseComponent Class

^f10cc7

Base class for creating component models. Parent: [`pydantic BaseModel`](https://docs.pydantic.dev/latest/)

### Attributes
- `id_ (str)`: A 32-char unique hash identifier for the node, automatically generated.
- `timestamp (str)`: The timestamp of when the node was created, automatically generated.

### Methods
- `class_name()`: Retrieves the name of the class.
- `to_json_str()`: Converts the component to a JSON string.
- `to_dict()`: Converts the component to a dictionary.
- `to_xml()`: Converts the component to an XML string.
- `to_pd_series()`: Converts the component to a Pandas Series.

### Special Methods for Field Annotations
- `_get_field_annotation()`: Overloaded method to get annotations for fields.
- `_field_has_attr()`: Checks if a field has a specific attribute.

## BaseNode Class

^5b7bda

Parent [[component#^f10cc7|BaseComponent]], meant for creating node models.

### Attributes
- `content (Any | None)`: The optional content of the node.
- `metadata (dict[str, Any])`: Additional metadata for the node.

### Class Methods for Object Creation
- `from_obj()`: Overloaded method to create a node instance from various types.

### Metadata Management
- `meta_get()`: Get a value from the metadata dictionary.
- `meta_change_key()`: Change a key in the metadata dictionary.
- `meta_insert()`: Insert a value into the metadata dictionary.
- `meta_merge()`: Merge additional metadata into the existing metadata dictionary.

## ConditionSource Enumeration

Enumeration for specifying the source type of a condition.

### Members
- `STRUCTURE`: Based on the structure.
- `EXECUTABLE`: Can be executed or evaluated.

## Condition Class

Abstract base class for defining conditions associated with edges. Parent  [`pydantic BaseModel`](https://docs.pydantic.dev/latest/)

### Attributes
- `source_type (ConditionSource)`: Specifies the type of source for the condition.

### Abstract Methods
- `__call__(*args, **kwargs)`: Evaluates the condition based on implemented logic.
