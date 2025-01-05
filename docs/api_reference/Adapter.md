# lionagi.protocols.adapter

```
Format conversion system between LionAGI data structures and external formats.

This module handles:
- Format conversion through Adapter protocol
- Format registry with AdapterRegistry
- Built-in adapters for common formats

Example:
    >>> from lionagi.protocols import Adapter, AdapterRegistry
    >>> # Convert to JSON
    >>> json_data = node.adapt_to("json")
    >>> # Load from DataFrame 
    >>> node = Node.adapt_from(df, "pd_dataframe")
```

## Adapter

Base protocol for format conversion.

```python
class Adapter(Protocol):
    """Format conversion protocol.
    
    Example:
        >>> class JsonAdapter(Adapter):
        ...     obj_key = "json"
        ...     def from_obj(cls, subj_cls, obj): ...
        ...     def to_obj(cls, subj): ...
    """
```

### Attributes

#### obj_key
Format identifier string.

Type:
- str

### Methods

#### classmethod from_obj(subj_cls, obj, /, **kwargs)
Convert from external format.

Parameters:
- **subj_cls** (*type[T]*) - Target class
- **obj** (*Any*) - Object to convert
- **kwargs** (*dict*) - Format options

Returns:
- dict | list[dict] - Internal format

Raises:
- TypeError - Invalid input format
- ValueError - Conversion error

#### classmethod to_obj(subj, /, **kwargs)
Convert to external format.

Parameters:
- **subj** (*T*) - Internal object
- **kwargs** (*dict*) - Format options

Returns:
- Any - External format

Raises:
- TypeError - Invalid input type
- ValueError - Conversion error

## AdapterRegistry

Registry for format adapters.

```python
class AdapterRegistry:
    """Format adapter registry.
    
    Example:
        >>> registry = AdapterRegistry()
        >>> registry.register(JsonAdapter)
        >>> data = registry.adapt_to(node, "json")
    """
```

### Methods

#### register(adapter)
Register format adapter.

Parameters:
- **adapter** (*type[Adapter]*) - Adapter class

Raises:
- TypeError - Missing required methods
- ValueError - Duplicate format key

Example:
```python
>>> registry.register(JsonAdapter)
```

#### adapt_from(subj_cls, obj, obj_key, **kwargs) 
Convert from external format.

Parameters:
- **subj_cls** (*type[T]*) - Target class
- **obj** (*Any*) - Object to convert
- **obj_key** (*str*) - Format key
- **kwargs** (*dict*) - Format options

Returns:
- T - Converted object

Raises:
- KeyError - Unknown format
- ValueError - Conversion error

Example:
```python
>>> node = registry.adapt_from(Node, data, "json")
```

#### adapt_to(subj, obj_key, **kwargs)
Convert to external format.

Parameters:
- **subj** (*T*) - Internal object
- **obj_key** (*str*) - Target format
- **kwargs** (*dict*) - Format options

Returns:
- Any - Converted object

Raises:
- KeyError - Unknown format
- ValueError - Conversion error

Example:
```python
>>> json_data = registry.adapt_to(node, "json")
```

## Built-in Adapters

### JsonAdapter
```python
class JsonAdapter(Adapter):
    """JSON string conversion.
    
    Example:
        >>> data = JsonAdapter.from_obj(Node, '{"key": "value"}')
        >>> json_str = JsonAdapter.to_obj(node)
    """
    obj_key = "json"
```

### PandasDataFrameAdapter
```python
class PandasDataFrameAdapter(Adapter):
    """Pandas DataFrame conversion.
    
    Example:
        >>> data = PandasDataFrameAdapter.from_obj(Node, df)
        >>> df = PandasDataFrameAdapter.to_obj(nodes)
    """
    obj_key = "pd_dataframe"
```

### FileAdapters
```python
class JsonFileAdapter(Adapter):
    """JSON file operations.
    
    Example:
        >>> data = JsonFileAdapter.from_obj(Node, "data.json")
        >>> JsonFileAdapter.to_obj(node, fp="data.json")
    """
    obj_key = ".json"
```

## Error Handling

```python
# Handle unknown format
try:
    result = registry.adapt_to(node, "unknown")
except KeyError as e:
    print(f"Unknown format: {e}")

# Handle conversion error
try:
    data = registry.adapt_from(Node, invalid_data, "json")
except ValueError as e:
    print(f"Conversion failed: {e}")
```
