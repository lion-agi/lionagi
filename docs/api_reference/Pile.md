---
type: api-reference
title: Pile System API Reference
created: 2025-01-04T18:00:00
updated: 2025-01-04T18:55:00
status: active
tags:
  - api-reference
  - lionagi
  - protocols
  - pile
aliases:
  - Pile System
sources:
  - "Local: /users/lion/lionagi/lionagi/protocols/generic/pile.py"
confidence: certain
---

# Pile System API Reference

## Overview

The Pile system provides thread-safe, type-safe collections with async support and format adapters. Core features:
- Type validation
- Order preservation via [[Progression System API Reference#Progression[E]|Progression]]
- Thread safety
- Format conversion

## Core Components

### Pile[E]

```python
class Pile(Element, Collective[E], Generic[E]):
    """Thread-safe collection manager."""
    
    collections: dict[IDType, T] = Field(default_factory=dict)
    item_type: set | None = Field(
        default=None,
        exclude=True
    )
    progression: Progression = Field(
        default_factory=Progression,
        exclude=True
    )
    strict_type: bool = Field(
        default=False,
        frozen=True
    )

    _adapter_registry: ClassVar[AdapterRegistry] = PileAdapterRegistry
    _lock: threading.Lock = PrivateAttr(default_factory=threading.Lock)
    _async_lock: asyncio.Lock = PrivateAttr(default_factory=asyncio.Lock)

    def __pydantic_extra__(self) -> dict[str, FieldInfo]:
        return {
            "_lock": Field(default_factory=threading.Lock),
            "_async": Field(default_factory=asyncio.Lock),
        }
```

### Core Operations

```python
@synchronized
def include(self, item: ID.ItemSeq | ID.Item, /) -> None:
    """Add new items."""
    item_dict = self._validate_pile(item)
    item_order = []
    for i in item_dict.keys():
        if i not in self.progression:
            item_order.append(i)
    self.progression.append(item_order)
    self.collections.update(item_dict)

@synchronized
def exclude(self, item: ID.Ref | ID.RefSeq) -> None:
    """Remove items."""
    item = to_list_type(item)
    exclude_list = []
    for i in item:
        if i in self:
            exclude_list.append(i)
    if exclude_list:
        self.pop(exclude_list)

@synchronized
def update(self, other: ID.ItemSeq | ID.Item, /) -> None:
    """Update with new items."""
    others = self._validate_pile(other)
    for i in others.keys():
        if i in self.collections:
            self.collections[i] = others[i]
        else:
            self.include(others[i])
```

### Async Support

```python
@async_synchronized
async def ainclude(self, item: ID.ItemSeq | ID.Item, /) -> None:
    """Async version of include()."""
    self._include(item)

@async_synchronized
async def aexclude(self, item: ID.ItemSeq | ID.Item, /) -> None:
    """Async version of exclude()."""
    self._exclude(item)

@async_synchronized
async def aupdate(self, other: ID.ItemSeq | ID.Item, /) -> None:
    """Async version of update()."""
    self._update(other)
```

### Format Adapters

```python
def to_df(self, columns: list[str] | None = None, **kwargs) -> pd.DataFrame:
    """Convert to DataFrame."""
    return self.adapt_to("pd_dataframe", columns=columns, **kwargs)

def to_csv_file(self, fp: str | Path, **kwargs) -> None:
    """Save to CSV file."""
    self.adapt_to(".csv", fp=fp, **kwargs)

def to_json_file(
    self,
    path_or_buf,
    use_pd: bool = False,
    mode="w",
    verbose=False,
    **kwargs,
) -> None:
    """Save to JSON file."""
```

## Implementation Examples

### Type-Safe Collection

```python
class TypedPile(Pile[CustomElement]):
    """Strongly typed pile."""
    
    def __init__(self, **kwargs):
        super().__init__(
            item_type=CustomElement,
            strict_type=True,
            **kwargs
        )

# Usage
pile = TypedPile()
pile.include(CustomElement())  # OK
pile.include(Element())  # Raises TypeError
```

### Async Operations

```python
async def process_items():
    pile = Pile[Element]()
    async with pile:
        await pile.ainclude(element)
        await pile.aupdate(other_elements)

    async for item in pile:
        await process(item)
```

### Format Conversion

```python
# Save to different formats
pile.to_csv_file("data.csv")
pile.to_json_file("data.json")

# Convert to DataFrame
df = pile.to_df(columns=["id", "value"])
```

## Best Practices

1. **Type Safety**
   - Use type parameter: `Pile[CustomType]`
   - Enable strict_type when needed
   - Validate inputs properly

2. **Thread Safety**
   - Use async context managers
   - Handle concurrent access
   - Use proper synchronization

3. **Memory Management**
   - Clear unused collections
   - Use format adapters efficiently
   - Handle large datasets carefully

## Related Components

### Core Dependencies
- [[Core Protocol Concepts]] - Base protocol interfaces
- [[Element]] - Core identifiable objects
- [[Generic Protocols]] - System overview

### Implementation References
- [[Progression System API Reference]] - Ordered sequences
- [[Log System API Reference]] - Logging system
- [[Event]] - Event handling
