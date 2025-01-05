# lionagi.protocols.generic.element

Core module providing identifiable objects with metadata support.

## Examples

```python
>>> from lionagi.protocols.generic import Element, IDType
>>> # Create basic element
>>> element = Element()
>>> element.id  # Automatically generated UUID
IDType('123e4567-e89b-12d3-a456-426614174000')
>>> element.metadata
{}

>>> # Element with custom data
>>> class User(Element):
...     name: str
...     age: int
... 
>>> user = User(name="Alice", age=30)
>>> user.created_at  # Timestamp automatically set
1704497180.45
```

## Classes

### class IDType
Thread-safe UUID-based identifier.

```python
class IDType:
    """Immutable UUIDv4-based identifier.
    
    Example:
        >>> id1 = IDType.create()  # New random ID
        >>> id2 = IDType.validate("123e4567-e89b-12d3-a456-426614174000")
        >>> id1 != id2
        True
    """
```

#### Methods

##### classmethod create()
Create new identifier with random UUIDv4.

Returns:
- IDType - New unique identifier

Example:
```python
>>> id1 = IDType.create()
>>> id2 = IDType.create()
>>> id1 != id2  # Always unique
True
```

##### classmethod validate(value)
Validate and convert to IDType.

Parameters:
- **value** (*str | UUID | IDType*) - Value to validate

Returns:
- IDType - Validated identifier

Raises:
- IDError - Invalid UUID format or nil UUID

Example:
```python
>>> # From string
>>> id1 = IDType.validate("123e4567-e89b-12d3-a456-426614174000")
>>> # From existing IDType
>>> id2 = IDType.validate(id1)
>>> id1 == id2
True
>>> # Invalid format
>>> IDType.validate("invalid")
Traceback (most recent call last):
    ...
IDError: Invalid UUID: invalid
```

### class Element
Base identifiable object with metadata.

```python
class Element(BaseModel, Observable):
    """Base class for identifiable objects with metadata support.
    
    Example:
        >>> elem = Element()
        >>> elem.id  # Auto-generated
        IDType('123e4567-e89b-12d3-a456-426614174000')
        >>> elem.created_at  # Auto-set timestamp
        1704497180.45
    """
```

#### Attributes

##### id
Unique identifier. Automatically generated and immutable.

Type:
- IDType

##### created_at
Creation timestamp (UTC). Automatically set and immutable.

Type:
- float

##### metadata  
Optional metadata dictionary.

Type:
- dict

#### Methods

##### classmethod from_dict(data, /)
Create instance from dictionary.

Parameters:
- **data** (*dict*) - Data to create instance from

Returns:
- Element - New instance

Example:
```python
>>> data = {
...     "metadata": {"key": "value"},
...     "other_field": 123
... }
>>> elem = Element.from_dict(data)
>>> elem.metadata
{'key': 'value'}
```

## Custom Elements

### Basic Extension
```python
class TypedElement(Element):
    """Element with typed value."""
    value: int = Field(gt=0)
    tags: list[str] = Field(default_factory=list)

# Create instance
elem = TypedElement(value=42, tags=["example"])
```

### Thread Safety
```python
class SafeElement(Element):
    """Thread-safe element operations."""
    _lock: threading.Lock = PrivateAttr(
        default_factory=threading.Lock
    )

    def update_safely(self, key: str, value: Any) -> None:
        """Thread-safe metadata update."""
        with self._lock:
            self.metadata[key] = value
```

### Versioning
```python
class VersionedElement(Element):
    """Element with version tracking."""
    version: int = Field(default=1, ge=1)
    
    def bump_version(self) -> None:
        """Increment version."""
        self.version += 1
```

## Common Patterns

### Metadata Management
```python
# Add metadata
element = Element()
element.metadata["category"] = "example"
element.metadata["tags"] = ["test", "demo"]

# Access metadata
category = element.metadata.get("category")
tags = element.metadata.get("tags", [])
```

### Serialization
```python
# Convert to dict
data = element.model_dump()
# {'id': '123e4567-...', 'created_at': 1704497180.45, 
#  'metadata': {'category': 'example'}}

# Create from dict  
new_element = Element.from_dict(data)
```

### Type Validation
```python
class ValidatedElement(Element):
    """Element with validation."""
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=150)
    email: str = Field(regex=r"^[a-z0-9]+@[a-z0-9]+\.[a-z]+$")

# Validation enforced
try:
    elem = ValidatedElement(name="", age=200)
except ValidationError as e:
    print(e)  # Field name too short, age too large
```

## Error Handling

### ID Errors
```python
try:
    IDType.validate("invalid-uuid")
except IDError as e:
    print(f"Invalid ID format: {e}")
```

### Validation Errors
```python
try:
    Element.from_dict({"metadata": "invalid"})
except ValidationError as e:
    print(f"Invalid data: {e}")
```

### Type Errors
```python
try:
    Element(metadata=["invalid"])
except ValueError as e:
    print(f"Invalid metadata: {e}")
```
