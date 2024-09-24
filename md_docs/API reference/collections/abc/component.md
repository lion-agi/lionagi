
# Class: `Element`

^bb802e

**Parent Class**: [`pydantic.BaseModel`](https://docs.pydantic.dev/latest/), [`ABC`](https://docs.python.org/3/library/abc.html)

**Description**:
`Element` is a base class for elements within the LionAGI system. It encapsulates essential attributes like a unique identifier and a timestamp.

**Attributes:**
- `ln_id` (str): A 32-character unique hash identifier.
- `timestamp` (str): The UTC timestamp of creation.

Always returns `True`.


---


# Class: `Component`

^ce462d

**Parent Class: [[#^bb802e|Element]]

**Description**:
`Component` represents a distinguishable, temporal entity in LionAGI. It encapsulates essential attributes and behaviors needed for individual components within the system's architecture. Each component is uniquely identifiable, with built-in version control and metadata handling.

**Attributes:**
- `ln_id` `(str)`: A unique identifier for the component.
- `timestamp` `(str)`: The UTC timestamp when the component was created.
- `metadata` `(dict)`: Additional metadata for the component.
- `extra_fields` `(dict)`: Additional fields for the component.
- `content` `(Any)`: Optional content of the component.
- `embedding` `(list[float])`: The optional embedding of the node.

## Methods

### `from_obj`

**Signature**:
```python
@singledispatchmethod
@classmethod
def from_obj(cls, obj: Any, /, **kwargs) -> T
```

**Parameters**:
- `obj` (Any): The input object to create `Component` instance(s) from.
- `**kwargs`: Additional keyword arguments to pass to the creation method.

**Return Values**:
- `T`: The created `Component` instance(s).

**Exceptions Raised**:
- [[Exceptions#^8519bb|LionTypeError]]: If the input type is not supported.

**Description**:
Creates `Component` instance(s) from various input types such as dictionaries, JSON strings, lists, `pandas` `Series`, `pandas` `DataFrames`, `Pydantic` models, `LlamaIndex` models, and `Langchain` models.

**Usage Examples**:
```python
# From a dictionary
component = Component.from_obj({"ln_id": "12345", "content": "example"})

# From a JSON string
component = Component.from_obj('{"ln_id": "12345", "content": "example"}')

# From a pandas Series
component = Component.from_obj(pd_series)

# pydantic models
component = Component.from_obj(pydantic_model)

# llama_index models
component = Component.from_obj(llama_index_node)

# langchain models
component = Component.from_obj(langchain_doc)

# From a list of valid items -> a list of Components
components = Component.from_obj([obj1, obj2])

# From a pd.DataFrame -> a list of Components
components = Component.from_obj(pd_dataframe)
```


### `class_name`

**Signature**:
```python
@property
def class_name() -> str
```

**Return Values**:
- `str`: The class name.

**Description**:
Gets the class name of the `Component`.

**Usage Examples**:
```python
# Example: Get the class name
name = component.class_name
```


###  `to_json_str`

**Signature**:
```python
def to_json_str(self, *args, **kwargs) -> str
```

**Return Values**:
- `str`: The JSON string representation of the `Component`.

**Description**:
Converts the `Component` to a JSON string.

**Usage Examples**:
```python
# Example: Convert the component to a JSON string
json_str = component.to_json_str()
```


### `to_dict`

*also check [[Type Conversion Lib#^479673|here]]

**Signature**:
```python
def to_dict(self, *args, **kwargs) -> dict[str, Any]
```

**Return Values**:
- `dict[str, Any]`: The dictionary representation of the `Component`.

**Description**:
Converts the `Component` to a dictionary.

**Usage Examples**:
```python
# Example: Convert the component to a dictionary
dict_repr = component.to_dict()
```

### `to_xml`

**Signature**:
```python
def to_xml(self, *args, **kwargs) -> str
```

**Return Values**:
- `str`: The XML string representation of the `Component`.

**Description**:
Converts the `Component` to an XML string.

**Usage Examples**:
```python
# Example: Convert the component to an XML string
xml_str = component.to_xml()
```

### `to_pd_series`

**Signature**:
```python
def to_pd_series(self, *args, pd_kwargs=None, **kwargs) -> Series
```

**Return Values**:
- `Series`: The pandas Series representation of the `Component`.

**Description**:
Converts the `Component` to a pandas Series.

**Usage Examples**:
```python
# Example: Convert the component to a pandas Series
pd_series = component.to_pd_series()
```

### `to_llama_index_node`

*also check [[llama_index_bridge#^6bd9d3|here]]

**Signature**:
```python
def to_llama_index_node(self, node_type: Type | str | Any = None, **kwargs) -> Any
```

**Parameters**:
- `node_type` (Type | str | Any, optional): The type of the node. Defaults to `None`.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `Any`: The LlamaIndex node representation of the `Component`.

**Description**:
Serializes the `Component` for LlamaIndex.

**Usage Examples**:
```python
# Example: Convert the component to a LlamaIndex node
llama_index_node = component.to_llama_index_node()
```

### `to_langchain_doc`

*also check [[langchain_bridge#^2fd882|here]]

**Signature**:
```python
def to_langchain_doc(self, **kwargs) -> Any
```

**Parameters**:
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `Any`: The Langchain document representation of the `Component`.

**Description**:
Serializes the `Component` for Langchain.

**Usage Examples**:
```python
# Example: Convert the component to a Langchain document
langchain_doc = component.to_langchain_doc()
```

### `add_field`

**Signature**:
```python
def add_field(self, field, value, annotation=None, **kwargs) -> None
```

**Parameters**:
- `field` (str): The name of the field.
- `value` (Any): The value of the field.
- `annotation` (Any, optional): The annotation for the field. Defaults to `None`.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `None`

**Description**:
Adds a field to the model.

**Usage Examples**:
```python
# Example: Add a field to the model
component.add_field("new_field", "value", str)
```


## Metadata Methods

### `_meta_pop`

**Signature**:
```python
def _meta_pop(self, indices, default=...) -> Any
```

**Parameters**:
- `indices` (list | str): The indices to pop from the metadata.
- `default` (Any, optional): The default value if the key is not found. Defaults to `...`.

**Return Values**:
- `Any`: The popped value from the metadata.

**Exceptions Raised**:
- `KeyError`: If the key is not found and no default is provided.

**Description**:
Pops a value from the metadata.

**Usage Examples**:
```python
# Example: Pop a value from the metadata
value = component._meta_pop(["key1", "key2"])
```

### `_meta_insert`

*also check [[Nested Data Lib#^3eb329|here]]

**Signature**:
```python
def _meta_insert(self, indices, value) -> None
```

**Parameters**:
- `indices` (list | str): The indices to insert into the metadata.
- `value` (Any): The value to insert.

**Return Values**:
- `None`

**Description**:
Inserts a value into the metadata.

**Usage Examples**:
```python
# Example: Insert a value into the metadata
component._meta_insert(["key1", "key2"], "value")
```

### `_meta_set`

*also check [[Nested Data Lib#^878481|here]]

**Signature**:
```python
def _meta_set(self, indices, value) -> None
```

**Parameters**:
- `indices` (list | str): The indices to set in the metadata.
- `value` (Any): The value to set.

**Return Values**:
- `None`

**Description**:
Sets a value in the metadata, inserting it if it does not already exist.

**Usage Examples**:
```python
# Example: Set a value in the metadata
component._meta_set(["key1", "key2"], "value")
```

### `_meta_get`

**Signature**:
```python
def _meta_get(self, indices, default=...) -> Any
```

**Parameters**:
- `indices` (list | str): The indices to get from the metadata.
- `default` (Any, optional): The default value if the key is not found. Defaults to `...`.

**Return Values**:
- `Any`: The value from the metadata.

**Description**:
Gets a value from the metadata.

**Usage Examples**:
```python
# Example: Get a value from the metadata
value = component._meta_get(["key1", "key2"])
```



### `_all_fields`

**Signature**:
```python
@property
def _all_fields() -> dict
```

**Return Values**:
- `dict`: All the fields of the model.

**Description**:
Gets all the fields of the model.

**Usage Examples**:
```python
# Example: Get all fields of the model
fields = component._all_fields
```

### `_field_annotations`

**Signature**:
```python
@property
def _field_annotations() -> dict
```

**Return Values**:
- `dict`: The annotations for each field in the model.

**Description**:
Gets the annotations for each field in the model.

**Usage Examples**:
```python
# Example: Get field annotations
annotations = component._field_annotations
```

### `_get_field_attr`

**Signature**:
```python
def _get_field_attr(self, k: str, attr: str, default: Any = False) -> Any
```

**Parameters**:
- `k` (str): The field name.
- `attr` (str): The attribute name.
- `default` (Any, optional): The default value if the attribute is not found. Defaults to `False`.

**Return Values**:
- `Any`: The value of the field attribute.

**Exceptions Raised**:
- `LionValueError`: If the field has no such attribute.
- `KeyError`: If the field is not found in the model fields.

**Description**:
Gets the value of a field attribute.

**Usage Examples**:
```python
# Example: Get the value of a field attribute
value = component._get_field_attr("field_name", "attribute_name")
```

### `_field_has_attr`

**Signature**:
```python
def _field_has_attr(self, k: str, attr: str) -> bool
```

**Parameters**:
- `k` (str): The field name.
- `attr` (str): The attribute name.

**Return Values**:
- `bool`: True if the field has the attribute, else False.

**Exceptions Raised**:
- `KeyError`: If the field is not found in the model fields.

**Description**:
Checks if a field has a specific attribute.

**Usage Examples**:
```python
# Example: Check if a field has a specific attribute
has_attr = component._field_has_attr("field_name", "attribute_name")
```
