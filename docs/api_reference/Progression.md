---
type: api-reference
title: Progression System API Reference
created: 2025-01-04T16:50:00
updated: 2025-01-04T18:40:00
status: active
tags:
  - api-reference
  - lionagi
  - protocols
  - progression
aliases:
  - Progression System
sources:
  - "Local: /users/lion/lionagi/lionagi/protocols/generic/progression.py"
confidence: certain
---

# Progression System API Reference

## Overview

The Progression system manages ordered sequences of [[Element#Element|Element]] identifiers, providing:
- Type-safe ordering
- List-like operations
- Thread safety
- Memory efficiency

## Core Component

### Progression[E]

```python
class Progression(Element, Ordering[E], Generic[E]):
    """Ordered sequence manager."""
    
    order: list[ID[E].ID] = Field(default_factory=list)
    name: str | None = Field(None)
    
    @field_validator("order", mode="before")
    def _validate_ordering(cls, value: Any) -> list[IDType]:
        """Ensure valid ID sequence."""
        return validate_order(value)

    @field_serializer("order")
    def _serialize_order(self, value: list[IDType]) -> list[str]:
        """Serialize IDs to strings."""
        return [str(x) for x in self.order]

    def include(self, item: Any, /) -> bool:
        """Add new IDs if not present."""
        try:
            refs = validate_order(item)
        except ValueError:
            return False
        if not refs:
            return True

        existing = set(self.order)
        appended = False
        for ref in refs:
            if ref not in existing:
                self.order.append(ref)
                existing.add(ref)
                appended = True
        return appended

    def exclude(self, item: Any, /) -> bool:
        """Remove occurrences of specified IDs."""
        try:
            refs = validate_order(item)
        except ValueError:
            return False
        if not refs:
            return True

        before = len(self.order)
        rset = set(refs)
        self.order = [x for x in self.order if x not in rset]
        return len(self.order) < before

    def append(self, item: Any, /) -> None:
        """Append IDs at the end."""
        if isinstance(item, Element):
            self.order.append(item.id)
            return
        refs = validate_order(item)
        self.order.extend(refs)

    def insert(self, index: int, item: ID.RefSeq, /) -> None:
        """Insert IDs at position."""
        item_ = validate_order(item)
        for i in reversed(item_):
            self.order.insert(index, ID.get_id(i))

    def pop(self, index: int = -1) -> IDType:
        """Remove and return ID at index."""
        try:
            return self.order.pop(index)
        except Exception as e:
            raise ItemNotFoundError(str(e)) from e

    def popleft(self) -> IDType:
        """Remove and return first ID."""
        if not self.order:
            raise ItemNotFoundError("No items in progression")
        return self.order.pop(0)

    def remove(self, item: Any, /) -> None:
        """Remove first occurrence of each ID."""
        try:
            refs = validate_order(item)
        except IDError:
            raise ItemNotFoundError("Invalid ID(s)")

        if not refs:
            return
        missing = [r for r in refs if r not in self.order]
        if missing:
            raise ItemNotFoundError(str(missing))
        self.order = [x for x in self.order if x not in refs]
```

### Operation Support

```python
def __add__(self, other: Any) -> "Progression[E]":
    """Return new combined progression."""
    new_refs = validate_order(other)
    return Progression(order=self.order + new_refs)

def __sub__(self, other: Any) -> "Progression[E]":
    """Return new progression excluding items."""
    refs = validate_order(other)
    remove_set = set(refs)
    new_order = [x for x in self.order if x not in remove_set]
    return Progression(order=new_order)

def __iadd__(self, other: Any) -> Self:
    """In-place addition."""
    self.append(other)
    return self

def __isub__(self, other: Any) -> Self:
    """In-place subtraction."""
    self.remove(other)
    return self
```

### List-Like Operations

```python
def __getitem__(self, key: int | slice) -> IDType | list[IDType]:
    """Get item(s) by index/slice."""
    if not isinstance(key, (int, slice)):
        raise TypeError(f"indices must be integers or slices, not {key.__class__.__name__}")
    try:
        a = self.order[key]
        if not a:
            raise ItemNotFoundError(f"index {key} item not found")
        return Progression(order=a) if isinstance(key, slice) else a
    except IndexError:
        raise ItemNotFoundError(f"index {key} item not found")

def __setitem__(self, key: int | slice, value: Any) -> None:
    """Set item(s) by index/slice."""
    refs = validate_order(value)
    if isinstance(key, slice):
        self.order[key] = refs
    else:
        try:
            self.order[key] = refs[0]
        except IndexError:
            self.order.insert(key, refs[0])

def __delitem__(self, key: int | slice) -> None:
    """Delete item(s) by index/slice."""
    del self.order[key]
```

## Implementation Examples

### Custom Progression

```python
class TypedProgression(Progression[CustomElement]):
    """Type-safe progression."""
    
    def validate_item(self, item: Any) -> None:
        if not isinstance(item, CustomElement):
            raise TypeError(f"Expected CustomElement, got {type(item)}")

    def append(self, item: Any) -> None:
        self.validate_item(item)
        super().append(item)
```

### Order Management

```python
# Create ordered sequence
prog = Progression[CustomElement](name="sequence")

# Add items
prog.append(element1)
prog.insert(0, element2)

# Remove items
removed = prog.pop()
prog.remove(element1)
```

## Best Practices

1. **Type Safety**
   - Use type parameter: `Progression[CustomType]`
   - Validate inputs with `validate_order()`
   - Handle ID conversion properly

2. **Memory Management**
   - Store only IDs, not full elements
   - Clear unused progressions
   - Use slicing for subsets

3. **Error Handling**
   - Handle missing items gracefully
   - Validate indices properly
   - Use ItemNotFoundError

## Related Components

### Core Dependencies
- [[Core Protocol Concepts]] - Base protocol interfaces
- [[Element]] - Core identifiable objects
- [[Generic Protocols]] - System overview

### Implementation References
- [[Pile System API Reference]] - Collection management
- [[Event]] - Event handling
