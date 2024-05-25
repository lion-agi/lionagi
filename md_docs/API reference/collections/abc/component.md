
### Class: `Element`

**Description**:
`Element` is a base class for elements within the LionAGI system. It encapsulates essential attributes like a unique identifier and a timestamp.

#### Attributes:
- `ln_id` (str): A 32-character unique hash identifier.
- `timestamp` (str): The UTC timestamp of creation.

### Method: `__init_subclass__`

**Signature**:
```python
def __init_subclass__(cls, **kwargs)
```

**Parameters**:
- `**kwargs`: Additional keyword arguments.

**Description**:
Registers the subclass in the `_init_class` dictionary if it is not already registered.

**Usage Examples**:
```python
class CustomElement(Element):
    pass
```

### Method: `__bool__`

**Signature**:
```python
def __bool__() -> bool
```

**Return Values**:
- `bool`: Always returns `True`.

**Usage Examples**:
```python
element = Element()
if element:
    print("Element is valid")
```

### Class: `Component`

**Description**:
`Component` represents a distinguishable, temporal entity in LionAGI. It encapsulates essential attributes and behaviors needed for individual components within the system's architecture. Each component is uniquely identifiable, with built-in version control and metadata handling.

#### Attributes:
- `ln_id` (str): A unique identifier for the component.
- `timestamp` (str): The UTC timestamp when the component was created.
- `metadata` (dict): Additional metadata for the component.
- `extra_fields` (dict): Additional fields for the component.
- `content` (Any): Optional content of the component.
- `embedding` (list[float]): The optional embedding of the node.

### Method: `from_obj`

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
- `LionTypeError`: If the input type is not supported.

**Description**:
Creates `Component` instance(s) from various input types such as dictionaries, JSON strings, lists, pandas Series, pandas DataFrames, Pydantic models, LlamaIndex models, and Langchain models.

**Usage Examples**:
```python
# Example 1: Create a Component from a dictionary
component = Component.from_obj({"ln_id": "12345", "content": "example"})

# Example 2: Create a Component from a JSON string
component = Component.from_obj('{"ln_id": "12345", "content": "example"}')
```

### Method: `_dispatch_from_obj`

**Signature**:
```python
@classmethod
def _dispatch_from_obj(cls, obj: Any, **kwargs) -> T
```

**Parameters**:
- `obj` (Any): The input object to create `Component` instance(s) from.
- `**kwargs`: Additional keyword arguments to pass to the creation method.

**Return Values**:
- `T`: The created `Component` instance(s).

**Description**:
Dispatches the `from_obj` method based on the input type.

**Usage Examples**:
```python
# Example: Dispatch from a dictionary
component = Component._dispatch_from_obj({"ln_id": "12345", "content": "example"})
```

### Method: `_from_llama_index`

**Signature**:
```python
@classmethod
def _from_llama_index(cls, obj: Any) -> T
```

**Parameters**:
- `obj` (Any): The input LlamaIndex object.

**Return Values**:
- `T`: The created `Component` instance.

**Description**:
Creates a `Component` instance from a LlamaIndex object.

**Usage Examples**:
```python
# Example: Create a Component from a LlamaIndex object
component = Component._from_llama_index(llama_index_obj)
```

### Method: `_from_langchain`

**Signature**:
```python
@classmethod
def _from_langchain(cls, obj: Any) -> T
```

**Parameters**:
- `obj` (Any): The input Langchain object.

**Return Values**:
- `T`: The created `Component` instance.

**Description**:
Creates a `Component` instance from a Langchain object.

**Usage Examples**:
```python
# Example: Create a Component from a Langchain object
component = Component._from_langchain(langchain_obj)
```

### Method: `_from_dict`

**Signature**:
```python
@classmethod
def _from_dict(cls, obj: dict, /, *args, **kwargs) -> T
```

**Parameters**:
- `obj` (dict): The input dictionary.
- `*args`: Positional arguments.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `T`: The created `Component` instance.

**Exceptions Raised**:
- `LionValueError`: If the dictionary is invalid for deserialization.

**Description**:
Creates a `Component` instance from a dictionary.

**Usage Examples**:
```python
# Example: Create a Component from a dictionary
component = Component._from_dict({"ln_id": "12345", "content": "example"})
```

### Method: `_process_langchain_dict`

**Signature**:
```python
@classmethod
def _process_langchain_dict(cls, dict_: dict) -> dict
```

**Parameters**:
- `dict_` (dict): The input dictionary containing Langchain-specific data.

**Return Values**:
- `dict`: The processed dictionary.

**Description**:
Processes a dictionary containing Langchain-specific data.

**Usage Examples**:
```python
# Example: Process a Langchain-specific dictionary
processed_dict = Component._process_langchain_dict(langchain_dict)
```

### Method: `_process_generic_dict`

**Signature**:
```python
@classmethod
def _process_generic_dict(cls, dict_: dict) -> dict
```

**Parameters**:
- `dict_` (dict): The input generic dictionary.

**Return Values**:
- `dict`: The processed dictionary.

**Description**:
Processes a generic dictionary.

**Usage Examples**:
```python
# Example: Process a generic dictionary
processed_dict = Component._process_generic_dict(generic_dict)
```

### Method: `_from_str`

**Signature**:
```python
@classmethod
def _from_str(cls, obj: str, /, *args, fuzzy_parse: bool = False, **kwargs) -> T
```

**Parameters**:
- `obj` (str): The input JSON string.
- `*args`: Positional arguments.
- `fuzzy_parse` (bool, optional): Whether to enable fuzzy parsing. Defaults to `False`.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `T`: The created `Component` instance.

**Exceptions Raised**:
- `LionValueError`: If the JSON string is invalid for deserialization.

**Description**:
Creates a `Component` instance from a JSON string.

**Usage Examples**:
```python
# Example: Create a Component from a JSON string
component = Component._from_str('{"ln_id": "12345", "content": "example"}')
```

### Method: `_from_list`

**Signature**:
```python
@classmethod
def _from_list(cls, obj: list, /, *args, **kwargs) -> list[T]
```

**Parameters**:
- `obj` (list): The input list.
- `*args`: Positional arguments.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `list[T]`: The list of created `Component` instances.

**Description**:
Creates a list of `Component` instances from a list of objects.

**Usage Examples**:
```python
# Example: Create a list of Components from a list
components = Component._from_list([obj1, obj2])
```

### Method: `_from_pd_series`

**Signature**:
```python
@classmethod
def _from_pd_series(cls, obj: Series, /, *args, pd_kwargs: dict | None = None, **kwargs) -> T
```

**Parameters**:
- `obj` (Series): The input pandas Series.
- `*args`: Positional arguments.
- `pd_kwargs` (dict, optional): Additional keyword arguments for pandas.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `T`: The created `Component` instance.

**Description**:
Creates a `Component` instance from a pandas Series.

**Usage Examples**:
```python
# Example: Create a Component from a pandas Series
component = Component._from_pd_series(pd_series)
```

### Method: `_from_pd_dataframe`

**Signature**:
```python
@classmethod
def _from_pd_dataframe(cls, obj: DataFrame, /, *args, pd_kwargs: dict | None = None, include_index=False, **kwargs) -> list[T]
```

**Parameters**:
- `obj` (DataFrame): The input pandas DataFrame.
- `*args`: Positional arguments.
- `pd_kwargs` (dict, optional): Additional keyword arguments for pandas.
- `include_index` (bool, optional): Whether to include the index in the metadata. Defaults to `False`.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `list[T]`: The list of created `Component` instances.

**Description**:
Creates a list of `Component` instances

 from a pandas DataFrame.

**Usage Examples**:
```python
# Example: Create a list of Components from a pandas DataFrame
components = Component._from_pd_dataframe(pd_dataframe)
```

### Method: `_from_base_model`

**Signature**:
```python
@classmethod
def _from_base_model(cls, obj, /, pydantic_kwargs=None, **kwargs) -> T
```

**Parameters**:
- `obj` (BaseModel): The input Pydantic BaseModel.
- `pydantic_kwargs` (dict, optional): Additional keyword arguments for Pydantic.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `T`: The created `Component` instance.

**Exceptions Raised**:
- `LionValueError`: If the Pydantic model is invalid for deserialization.

**Description**:
Creates a `Component` instance from a Pydantic BaseModel.

**Usage Examples**:
```python
# Example: Create a Component from a Pydantic BaseModel
component = Component._from_base_model(pydantic_model)
```

### Method: `class_name`

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

### Method: `_class_name`

**Signature**:
```python
@classmethod
def _class_name(cls) -> str
```

**Return Values**:
- `str`: The class name.

**Description**:
Gets the class name of the `Component`.

**Usage Examples**:
```python
# Example: Get the class name
name = Component._class_name()
```

### Method: `to_json_str`

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

### Method: `to_dict`

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

### Method: `to_xml`

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

### Method: `to_pd_series`

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

### Method: `to_llama_index_node`

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

### Method: `to_langchain_doc`

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

### Method: `_add_last_update`

**Signature**:
```python
def _add_last_update(self, name) -> None
```

**Parameters**:
- `name` (str): The name of the field to update.

**Return Values**:
- `None`

**Description**:
Adds the last update timestamp to the metadata.

**Usage Examples**:
```python
# Example: Add the last update timestamp for a field
component._add_last_update("field_name")
```

### Method: `_meta_pop`

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

### Method: `_meta_insert`

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

### Method: `_meta_set`

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

### Method: `_meta_get`

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

### Method: `__setattr__`

**Signature**:
```python
def __setattr__(self, name, value) -> None
```

**Parameters**:
- `name` (str): The name of the attribute.
- `value` (Any): The value to set.

**Return Values**:
- `None`

**Description**:
Sets an attribute, updating the metadata with the last update timestamp.

**Usage Examples**:
```python
# Example: Set an attribute
component.attribute = "value"
```

### Method: `_add_field`

**Signature**:
```python
def _add_field(
    self,
    field: str,
    annotation: Any = None,
    default: Any = None,
    value: Any = None,
    field_obj: Any = None,
    **kwargs,
) -> None
```

**Parameters**:
- `field` (str): The name of the field.
- `annotation` (Any, optional): The annotation for the field. Defaults to `None`.
- `default` (Any, optional): The default value for the field. Defaults to `None`.
- `value` (Any, optional): The value of the field. Defaults to `None`.
- `field_obj` (Any, optional): The field object. Defaults to `None`.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `None`

**Description**:
Adds a field to the model after initialization.

**Usage Examples**:
```python
# Example: Add a field to the model
component._add_field("new_field", str, default="default_value")
```

### Method: `add_field`

**Signature**:
```python
def add_field(self, field, value, annotation=None, **kwargs) -> None
```

**Parameters**:
- `field` (str): The name of the field.
-

 `value` (Any): The value of the field.
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

### Method: `_all_fields`

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

### Method: `_field_annotations`

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

### Method: `_get_field_attr`

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
- `FieldError`: If the field has no such attribute.
- `KeyError`: If the field is not found in the model fields.

**Description**:
Gets the value of a field attribute.

**Usage Examples**:
```python
# Example: Get the value of a field attribute
value = component._get_field_attr("field_name", "attribute_name")
```

### Method: `_get_field_annotation`

**Signature**:
```python
@singledispatchmethod
def _get_field_annotation(self, field_name: Any) -> Any
```

**Parameters**:
- `field_name` (Any): The field name.

**Return Values**:
- `Any`: The field annotation.

**Exceptions Raised**:
- `LionTypeError`: If the field name type is not supported.

**Description**:
Gets the annotation for a field.

**Usage Examples**:
```python
# Example: Get the annotation for a field
annotation = component._get_field_annotation("field_name")
```

### Method: `_field_has_attr`

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

### Method: `__str__`

**Signature**:
```python
def __str__() -> str
```

**Return Values**:
- `str`: The string representation of the `Component`.

**Description**:
Gets the string representation of the `Component`.

**Usage Examples**:
```python
# Example: Get the string representation of the component
print(str(component))
```

### Method: `__repr__`

**Signature**:
```python
def __repr__() -> str
```

**Return Values**:
- `str`: The string representation of the `Component`.

**Description**:
Gets the string representation of the `Component`.

**Usage Examples**:
```python
# Example: Get the string representation of the component
print(repr(component))
```

### Method: `__len__`

**Signature**:
```python
def __len__() -> int
```

**Return Values**:
- `int`: The length of the `Component`.

**Description**:
Gets the length of the `Component`.

**Usage Examples**:
```python
# Example: Get the length of the component
length = len(component)
```

### Function: `get_lion_id`

**Signature**:
```python
def get_lion_id(item: LionIDable) -> str
```

**Parameters**:
- `item` (LionIDable): The item to get the Lion ID from.

**Return Values**:
- `str`: The Lion ID of the item.

**Exceptions Raised**:
- `LionTypeError`: If the item is not a single LionIDable object.

**Description**:
Gets the Lion ID of an item.

**Usage Examples**:
```python
# Example: Get the Lion ID of an item
lion_id = get_lion_id(item)
```
