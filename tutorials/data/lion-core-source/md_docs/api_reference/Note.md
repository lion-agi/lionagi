# Note API Documentation

## Overview

The `Note` class is a flexible container for managing nested dictionary data structures in the Lion framework. It provides a rich set of methods for manipulating and accessing nested data, making it ideal for storing and managing complex, hierarchical information.

## Class Definition

```python
class Note(BaseModel, Container):
    """A container for managing nested dictionary data structures."""
```

## Attributes

- `content: dict[str, Any]` - The internal dictionary storing the nested data structure.

## Constructor

```python
def __init__(self, **kwargs):
```

Initialize a Note instance with the provided keyword arguments as initial content.

## Methods

### Data Manipulation

#### `pop`

```python
def pop(self, indices: list[str] | str, default: Any = LN_UNDEFINED, /) -> Any:
```

Remove and return an item from the nested structure.

#### `insert`

```python
def insert(self, indices: list[str] | str, value: Any, /) -> None:
```

Insert a value into the nested structure at the specified indices.

#### `set`

```python
def set(self, indices: list[str] | str, value: Any, /) -> None:
```

Set a value in the nested structure at the specified indices.

#### `get`

```python
def get(self, indices: list[str] | str, default: Any = LN_UNDEFINED, /) -> Any:
```

Get a value from the nested structure at the specified indices.

#### `update`

```python
def update(self, items: Any, indices: list[str | int] = None, /):
```

Update the Note with new items, optionally at specific indices.

#### `clear`

```python
def clear(self):
```

Clear the content of the Note.

### Data Access

#### `keys`

```python
def keys(self, /, flat: bool = False) -> list:
```

Get the keys of the Note, optionally flattened.

#### `values`

```python
def values(self, /, flat: bool = False):
```

Get the values of the Note, optionally flattened.

#### `items`

```python
def items(self, /, flat: bool = False):
```

Get the items (key-value pairs) of the Note, optionally flattened.

### Conversion and Representation

#### `to_dict`

```python
def to_dict(self, **kwargs) -> dict[str, Any]:
```

Convert the Note to a dictionary.

#### `from_dict`

```python
@classmethod
def from_dict(cls, kwargs) -> "Note":
```

Create a Note from a dictionary.

#### `__str__`

```python
def __str__(self) -> str:
```

Return a string representation of the Note.

#### `__repr__`

```python
def __repr__(self) -> str:
```

Return a detailed string representation of the Note.

### Container Operations

#### `__contains__`

```python
def __contains__(self, indices: str | list) -> bool:
```

Check if the Note contains the specified indices.

#### `__len__`

```python
def __len__(self) -> int:
```

Return the number of top-level keys in the Note.

#### `__iter__`

```python
def __iter__(self):
```

Return an iterator over the top-level keys of the Note.

#### `__next__`

```python
def __next__(self):
```

Return the next top-level key in the Note.

### Item Access

#### `__getitem__`

```python
def __getitem__(self, *indices) -> Any:
```

Get an item or nested item from the Note using indexing.

#### `__setitem__`

```python
def __setitem__(self, indices: str | tuple, value: Any) -> None:
```

Set an item or nested item in the Note using indexing.

## Usage Examples

### Creating a Note

```python
from lion_core.generic.note import Note, note

# Create a Note instance
my_note = Note(name="John Doe", age=30, address={"city": "New York", "country": "USA"})

# Use the note helper function
another_note = note(title="Meeting Notes", date="2024-03-15", attendees=["Alice", "Bob"])
```

### Accessing and Modifying Data

```python
# Get values
name = my_note.get("name")
city = my_note.get(["address", "city"])

# Set values
my_note.set("email", "john@example.com")
my_note.set(["address", "zip"], "10001")

# Using indexing
my_note["phone"] = "555-1234"
country = my_note["address"]["country"]

# Remove values
removed_age = my_note.pop("age")

# Update multiple values
my_note.update({"occupation": "Engineer", "skills": ["Python", "JavaScript"]})
```

### Nested Operations

```python
# Insert nested data
my_note.insert(["education", "university"], "MIT")

# Update nested data
my_note.update({"grades": {"math": 95, "physics": 88}}, indices=["education"])

# Access nested data
math_grade = my_note.get(["education", "grades", "math"])
```

### Iteration and Checks

```python
# Iterate over top-level keys
for key in my_note:
    print(key)

# Check if a key or path exists
if "address" in my_note:
    print("Address information is available")

if ["education", "university"] in my_note:
    print("University information is available")

# Get all keys (flat or nested)
all_keys = my_note.keys(flat=True)

# Get all items (flat or nested)
all_items = my_note.items(flat=True)
```

### Conversion

```python
# Convert to dictionary
note_dict = my_note.to_dict()

# Create from dictionary
new_note = Note.from_dict(note_dict)
```

## Best Practices

1. Use the `note` helper function for quick Note creation with a clean syntax.
2. Prefer using the `get` method with a default value to safely access potentially missing data.
3. Use the `update` method for bulk updates, especially when modifying nested structures.
4. When working with deeply nested structures, consider using the flattened views (`keys(flat=True)`, `items(flat=True)`) for easier data manipulation.
5. Use type hints when working with Notes to improve code readability and catch potential type errors early.
6. When subclassing `Note`, ensure to properly handle the `content` attribute to maintain the class's functionality.

## Notes

- The `Note` class is designed to be flexible and can handle arbitrary levels of nesting.
- When using `pop`, `insert`, `set`, or `get` methods, you can provide the indices as either a list of strings or a single string for top-level access.
- The `update` method can handle various input types, including dictionaries, strings (which it attempts to parse as JSON), and other Note objects.
- The `LN_UNDEFINED` constant is used to distinguish between explicitly set `None` values and missing values.
- Flattened views of keys, values, and items use the `|` character as a separator for nested keys.
