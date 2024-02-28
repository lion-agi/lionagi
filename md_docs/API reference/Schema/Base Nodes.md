---
tags:
  - Tool
  - API
  - BaseObj
created: 2024-02-26
completed: true
---

# Base Nodes API Reference



## BaseComponent

> Child class of `pydantic.BaseModel` and `abc.ABC`

The foundational model for creating components with shared functionality and attributes.

### Attributes

- `id_`: Unique identifier, automatically generated to ensure uniqueness.
- `timestamp`: Timestamp for creation or modification, defaulting to the current time if not specified.
- `metadata`: A flexible dictionary for storing additional information related to the component.

### Class Methods

#### `class_name() -> str`

Returns the class name of the component. Useful for logging, debugging, or when implementing factory patterns.

**Example:**

```python
print(BaseComponent.class_name())  # Output: BaseComponent
```

#### `from_dict(data: Dict[str, Any], **kwargs) -> T`

Creates an instance from a dictionary, allowing for easy deserialization from data sources that provide dictionaries.

**Example:**

```python
data = {"id_": "123", "metadata": {"author": "John Doe"}}
component = BaseComponent.from_dict(data)
print(component.id_)  # Output: 123
```

#### `from_json(json_str: str, **kwargs) -> T`

Deserializes a component from a JSON string. This method is particularly useful when dealing with JSON data from web APIs or files.

**Example:**

```python
json_str = '''{"id_": "123", "metadata": {"author": "John Doe"}}'''
component = BaseComponent.from_json(json_str)
print(component.metadata)  # Output: {'author': 'John Doe'}
```

#### `from_pd_series(pd_series: pd.Series, pd_kwargs=None, **kwargs) -> T`

Creates an instance from a pandas Series, facilitating integration with pandas data structures commonly used in data analysis.

**Example:**

```python
import pandas as pd
series = pd.Series({"id_": "123", "metadata": {"author": "John Doe"}})
component = BaseComponent.from_pd_series(series)
print(component.timestamp)  # Example output: 2021-01-01T00:00:00
```

### Instance Methods

#### `to_json(*args, **kwargs) -> str`

Serializes the instance to a JSON string, making it easy to store or transmit the component's data.

**Example:**

```python
component = BaseComponent(id_="123", metadata={"author": "John Doe"})
print(component.to_json())  # Output: '''{"id_": "123", "metadata": {"author": "John Doe"}}'''
```

#### `to_dict(*args, **kwargs) -> Dict[str, Any]`

Serializes the instance to a dictionary, useful for when you need to manipulate the component's data programmatically.

**Example:**

```python
component = BaseComponent(id_="123", metadata={"author": "John Doe"})
print(component.to_dict())  # Output: {'id_': '123', 'metadata': {'author': 'John Doe'}}
```

#### `to_xml() -> str`

Serializes the instance to an XML string, offering an alternative format for data interchange, especially in systems where XML is preferred.

**Example:**

```python
component = BaseComponent(id_="123", metadata={"author": "John Doe"})
print(component.to_xml())  # Output: <BaseComponent><id_>123</id_><metadata><author>John Doe</author></metadata></BaseComponent>
```

#### `to_pd_series(*args, pd_kwargs=None, **kwargs) -> pd.Series`

Converts the instance into a pandas Series, facilitating the use of the component's data within pandas for analysis or manipulation.

**Example:**

```python
component = BaseComponent(id_="123", metadata={"author": "John Doe"})
series = component.to_pd_series()
print(series)  # Output: id_ 123, metadata {'author': 'John Doe'}
```

#### `copy(*args, **kwargs)`

Creates a deep copy of the instance, optionally updating attributes with provided keyword arguments. This is useful for creating variations of components without modifying the original instance.

**Example:**

```python
original = BaseComponent(metadata={"author": "John Doe"})
copy = original.copy(metadata={"author": "Jane Doe"})
print(original.metadata, copy.metadata)  # Output: {'author': 'John Doe'} {'author': 'Jane Doe'}
```

### Metadata Management

These methods provide a way to interact with the `metadata` attribute, allowing for inspection, modification, and management of metadata keys and values.

(For brevity, examples for metadata management methods are omitted but should follow a similar structure to the examples provided above, demonstrating how to interact with the `metadata` dictionary of a `BaseComponent` instance.)


## BaseNode

> Child class of [[Base Nodes#^b7a549|BaseComponent]]

Extends `BaseComponent` by adding a `content` attribute for storing the node's data, supporting various data types.

### Attributes

- Inherits all attributes from `BaseComponent`.
- `content`: `str | Dict[str, Any] | None | Any` - The content of the node, which can be a string, dictionary, other data types, or `None`.

### Instance Methods

#### `content_str() -> str`

Provides a string representation of the node's content, facilitating easy display or logging of the content.

**Example:**

```python
node = BaseNode(content={"key": "value"})
print(node.content_str())  # Output: '''{"key": "value"}'''
```

## BaseRelatableNode

^614ddc

> Child class of [[Base Nodes#^9e015a|BaseNode]]

Enhances `BaseNode` by adding functionality to manage relationships between nodes, such as adding or removing related nodes.

### Attributes

- Inherits all attributes from `BaseNode`.
- `related_nodes`: `List[str]` - Identifiers of other nodes that are related to this one.
- `label`: `str | None` - An optional label for the node.

### Instance Methods

#### `add_related_node(node_id: str) -> bool`

Adds a node ID to the list of related nodes if it's not already present, indicating a new relationship.

**Example:**

```python
node = BaseRelatableNode(content="Example content")
node.add_related_node("node123")
print(node.related_nodes)  # Output: ['node123']
```

#### `remove_related_node(node_id: str) -> bool`

Removes a node ID from the list of related nodes, effectively ending that relationship.

**Example:**

```python
node = BaseRelatableNode(related_nodes=["node123", "node456"])
node.remove_related_node("node123")
print(node.related_nodes)  # Output: ['node456']
```



## Tool

^0c90e6

> Child class of [[Base Nodes#^614ddc|BaseRelatableNode]]

Represents a specialized node that includes a functional aspect, such as a task or operation, with attributes for storing associated functionality and documentation.

### Attributes

- Inherits all attributes from `BaseRelatableNode`.
- `func`: `Any` - A reference to the function associated with the tool. This could be any callable object.
- `manual`: `Any | None` - Optional attribute for storing a manual or documentation related to the tool's function.
- `parser`: `Any | None` - Optional attribute for storing a parser that can be used with the tool's function.

### Instance Methods

#### `serialize_func(func) -> str`

A custom serialization method for the `func` attribute, designed to store the function's name as a string. This is particularly useful for logging or displaying the function associated with a tool without executing it.

**Example:**

```python
def example_function():
    return "This is an example function."

tool = Tool(func=example_function)
print(tool.serialize_func(tool.func))  # Output: example_function
```

This class extends the capabilities of `BaseRelatableNode` by incorporating functional aspects, making it suitable for representing tools or operations within a system that are related to other nodes.