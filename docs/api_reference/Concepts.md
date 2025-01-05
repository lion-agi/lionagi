# lionagi.protocols.concepts

```
Core protocols and abstract base classes defining fundamental interfaces in LionAGI.

This module provides:
- Base identifiable objects (Observable ABC)
- Event monitoring (Observer Protocol)
- Collection handling (Collective Protocol)
- Resource management (Manager Protocol)

Example:
    >>> from lionagi.protocols.concepts import Observable
    >>> class CustomElement(Observable):
    ...     def __init__(self):
    ...         super().__init__()
    ...         self.id = IDType.create()
```

## Observable

Abstract base class for identifiable objects.

```python
class Observable(ABC):
    """Abstract base class requiring unique identification.
    
    All subclasses must have an 'id' attribute of type IDType.
    
    Example:
        >>> class CustomElement(Observable):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.id = IDType.create()
        >>> elem = CustomElement()
        >>> elem.id  # Required by ABC
        'elem_a1b2c3d4'
    """
```

### Attributes

#### id
Unique object identifier. Required by ABC.

Type:
- IDType

Example:
```python
>>> class InvalidElement(Observable):
...     pass  # Missing required 'id'
>>> elem = InvalidElement()  # Raises TypeError
Traceback (most recent call last):
    ...
TypeError: Can't instantiate abstract class InvalidElement without 'id' attribute
```

## Observer

Protocol for event monitoring.

```python
class Observer(Protocol):
    """Protocol for event monitoring.
    
    Example:
        >>> class CustomObserver(Observer):
        ...     def observe(self, event):
        ...         print(f"Event: {event.id}")
    """
```

### Methods

#### observe(event)
Handle observed event.

Parameters:
- **event** (*Event*) - Event to process

## Manager

Protocol for resource management.

```python
class Manager(Observer):
    """Protocol for resource management.
    
    Example:
        >>> class ResourceManager(Manager):
        ...     def __init__(self):
        ...         self.resources = {}
        ...     def observe(self, event):
        ...         self.resources[event.id] = event.status
    """
```

## Collective[E]

Protocol for type-safe collections.

```python
class Collective(Protocol, Generic[E]):
    """Protocol for collection handling.
    
    Example:
        >>> class ItemCollection(Collective[Item]):
        ...     def __init__(self):
        ...         self.items = {}
        ...     def include(self, item: Item):
        ...         self.items[item.id] = item
        ...     def exclude(self, item: Item):
        ...         del self.items[item.id]
    """
```

### Methods

#### include(item, /)
Add item to collection.

Parameters:
- **item** (*E*) - Item to add

Example:
```python
>>> collection = ItemCollection()
>>> item = Item(id='item_1')
>>> collection.include(item)
```

#### exclude(item, /)
Remove item from collection.

Parameters:
- **item** (*E*) - Item to remove

Example:
```python
>>> collection.exclude(item)
```

## Error Handling

```python
# Handle missing 'id' attribute (ABC requirement)
try:
    class BadElement(Observable):
        pass
    elem = BadElement()  # Missing required 'id'
except TypeError as e:
    print(f"ABC requirement not met: {e}")

# Handle invalid item type
try:
    collection.include(invalid_item)
except TypeError as e:
    print(f"Invalid item type: {e}")
```
