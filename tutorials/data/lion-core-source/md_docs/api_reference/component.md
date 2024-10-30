# Component API Documentation

## Overview

The `Component` class is an extended base class for components in the Lion framework. It inherits from the `Element` class and provides additional functionality for managing metadata, content, and dynamic fields. This class is designed to be flexible and extensible, allowing for easy creation and manipulation of complex data structures.

## Class Definition

```python
class Component(Element):
    """Extended base class for components in the Lion framework."""
```

## Attributes

- `metadata: Note` - Additional metadata for the component
- `content: Any` - The main content of the Component
- `embedding: list[float]` - A list of floats representing an embedding
- `extra_fields: dict[str, Any]` - A dictionary of additional fields

## Properties

### `all_fields`

```python
@property
def all_fields(self) -> dict[str, FieldInfo]:
```

Returns a dictionary containing all fields, including model fields and extra fields.

## Methods

### Field Management

#### `add_field`

```python
def add_field(
    self,
    field_name: str,
    value: Any = LN_UNDEFINED,
    annotation: Any = LN_UNDEFINED,
    field_obj: FieldInfo = LN_UNDEFINED,
    **kwargs
) -> None:
```

Adds a new field to the component's extra fields.

- `field_name`: The name of the field to add
- `value`: The value of the field (default: `LN_UNDEFINED`)
- `annotation`: Type annotation for the field (default: `LN_UNDEFINED`)
- `field_obj`: A pre-configured FieldInfo object (default: `LN_UNDEFINED`)
- `**kwargs`: Additional keyword arguments for Field configuration

Raises `LionValueError` if the field already exists.

#### `update_field`

```python
def update_field(
    self,
    field_name: str,
    value: Any = LN_UNDEFINED,
    annotation: Any = LN_UNDEFINED,
    field_obj: FieldInfo | Any = LN_UNDEFINED,
    **kwargs
) -> None:
```

Updates an existing field or creates a new one if it doesn't exist.

- `field_name`: The name of the field to update or create
- `value`: The new value for the field (default: `LN_UNDEFINED`)
- `annotation`: Type annotation for the field (default: `LN_UNDEFINED`)
- `field_obj`: A pre-configured FieldInfo object (default: `LN_UNDEFINED`)
- `**kwargs`: Additional keyword arguments for Field configuration

Raises `ValueError` if both 'default' and 'default_factory' are provided in kwargs.

### Conversion Methods

#### `to_dict`

```python
def to_dict(self, **kwargs) -> dict:
```

Converts the component to a dictionary representation.

- `**kwargs`: Additional arguments to pass to `model_dump`

Returns a dictionary representation of the component.

#### `to_note`

```python
def to_note(self, **kwargs) -> Note:
```

Converts the component to a `Note` object.

#### `from_dict`

```python
@classmethod
def from_dict(cls, data: dict, **kwargs) -> T:
```

Creates a component instance from a dictionary.

- `data`: The dictionary containing component data
- `**kwargs`: Additional arguments for Pydantic model validation

Returns an instance of the Component class or its subclass.

### Converter Methods

#### `get_converter_registry`

```python
@classmethod
def get_converter_registry(cls) -> ComponentConverterRegistry:
```

Gets the converter registry for the class.

#### `convert_to`

```python
def convert_to(self, key: str = "dict", /, **kwargs: Any) -> Any:
```

Converts the component to a specified type using the ConverterRegistry.

#### `convert_from`

```python
@classmethod
def convert_from(cls, obj: Any, key: str = "dict", /, **kwargs) -> T:
```

Converts data to create a new component instance using the ConverterRegistry.

#### `register_converter`

```python
@classmethod
def register_converter(cls, key: str, converter: Type[Converter]) -> None:
```

Registers a new converter. Can be used for both a class and/or an instance.

### Field Attribute Management

#### `field_setattr`

```python
def field_setattr(self, field_name: str, attr: Any, value: Any, /) -> None:
```

Sets the value of a field attribute.

#### `field_hasattr`

```python
def field_hasattr(self, field_name: str, attr: str, /) -> bool:
```

Checks if a field has a specific attribute.

#### `field_getattr`

```python
def field_getattr(self, field_name: str, attr: str, default: Any = LN_UNDEFINED, /) -> Any:
```

Gets the value of a field attribute.

#### `_field_annotation`

```python
def _field_annotation(self, field_name: Any, /) -> dict[str, Any]:
```

Gets field annotation for a given field.

## Usage Examples

### Creating a Component

```python
from lion_core.generic.component import Component
from lion_core.generic.note import Note

# Create a basic component
component = Component(content="Hello, World!")
```

### Adding and Updating Fields

```python
# Add a new field
component.add_field("priority", value=1, annotation=int)

# Update an existing field
component.update_field("priority", value=2)

# Add a field with custom configuration
component.add_field("tags", value=["important", "urgent"], annotation=list[str])
```

### Converting Components

```python
# Convert component to dictionary
component_dict = component.to_dict()

# Convert dictionary to component
new_component = Component.from_dict(component_dict)

# Convert component to Note
component_note = component.to_note()
```

### Using Field Attribute Management

```python
# Set a field attribute
component.field_setattr("priority", "description", "Task priority")

# Check if a field has an attribute
has_description = component.field_hasattr("priority", "description")

# Get a field attribute
priority_description = component.field_getattr("priority", "description")
```

### Updating MetaData

```python
# set an item to metadata
component.metadata["config", "version"] = 1

# change an value
component.metadata["config", "version"] = 2

# get a value with default value
component.metadata.get(["config", "spec"], None)

```


## Best Practices

1. Always use type annotations when adding or updating fields to ensure type safety.
2. Utilize the `metadata` attribute for storing additional information about the component.
3. When converting between different formats, use the built-in conversion methods (`to_dict`, `from_dict`, etc.) to ensure consistency.
4. Take advantage of the dynamic field management capabilities, but use them judiciously to maintain code clarity.
5. When subclassing `Component`, override the `from_dict` method if you need custom deserialization logic.

## Notes

- The `Component` class uses Pydantic for data validation and serialization.
- The `LN_UNDEFINED` constant is used to represent undefined values and is distinct from `None`.
- The class supports dynamic field management, allowing for flexible data structures.
- Converter functionality allows for easy transformation between different data formats.
