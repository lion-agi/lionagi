
## Class: `Pile`

^0206c8

**Parent Class:**  [[Component#^bb802e|Element]], [[API reference/collections/abc/Concepts#^14e4ff|Record]]


**Description**:
`Pile` is a collection class for managing `Element` objects. It facilitates ordered and type-validated storage and access, supporting both index-based and key-based retrieval.

Attributes:
- `use_obj` (bool): If `True`, treat `Record` and `Ordering` as objects.
- `pile` `(dict[str, T])`: Maps unique identifiers to items.
- `item_type` `(set[Type[Element]] | None)`: Allowed item types.
- `name` (str | None): Optional name for the pile.
- `order` `(list[str])`: Order of item identifiers.
- `index` (Any): Index for the pile.
- `engines` `(dict[str, Any])`: Engines for querying or other operations.
- `query_response` (Any): Responses from queries.
- `tools` (dict): Tools for pile operations.

###  `__init__`

**Signature**:
```python
def __init__(self, items=None, item_type=None, order=None, use_obj=None)
```

**Parameters**:
- `items` (optional): Initial items to include in the pile.
- `item_type` (optional): Allowed types of items in the pile.
- `order` (optional): The order of items.
- `use_obj` (optional): Whether to treat `Record` and `Ordering` as objects.

**Usage Examples**:
```python
# Example 1: Create a Pile with default parameters
pile_instance = Pile()

# Example 2: Create a Pile with specified items and item types
pile_instance = Pile(items=my_items, item_type={Element})
```

###  `__getitem__`

**Signature**:
```python
def __getitem__(self, key) -> T | "Pile[T]"
```

**Parameters**:
- `key`: Key to retrieve items.

**Return Values**:
- `T | Pile[T]`: The requested item(s). Single items returned directly, multiple items returned in a new `Pile` instance.

**Exceptions Raised**:
- [[Exceptions#^ee9dbb|ItemNotFoundError]]: If requested item(s) not found.
- [[Exceptions#^8519bb|LionTypeError]]: If provided key is invalid.

**Description**:
Retrieves items from the pile using a key. Supports multiple types of key access, including index, slice, and `LionID`.

**Usage Examples**:
```python
# Example: Retrieve an item by index
item = pile_instance[0]

# Example: Retrieve items by slice
items = pile_instance[0:5]

# Example: Retrieve an item by LionID
item = pile_instance["item_id"]
```

###  `__setitem__`

**Signature**:
```python
def __setitem__(self, key, item) -> None
```

**Parameters**:
- `key`: Key to set items. Can be index, slice, LionID, LionIDable.
- `item`: Item(s) to set. Can be single item or collection.

**Exceptions Raised**:
- `ValueError`: Length mismatch or multiple items to single key.
- `LionTypeError`: Item type doesn't match allowed types.

**Description**:
Sets new values in the pile using various key types. Handles single/multiple assignments and ensures type consistency.

**Usage Examples**:
```python
# Example: Set an item at a specific index
pile_instance[0] = new_item

# Example: Set multiple items at specific indices
pile_instance[0:2] = [new_item1, new_item2]
```

###  `__contains__`

**Signature**:
```python
def __contains__(self, item: Any) -> bool
```

**Parameters**:
- `item`: Item(s) to check. Can be single item or collection.

**Return Values**:
- `bool`: True if all items are found, False otherwise.

**Description**:
Checks if item(s) are present in the pile. Accepts individual items and collections.

**Usage Examples**:
```python
# Example: Check if an item is in the pile
if "item_id" in pile_instance:
    print("Item is in the pile")
```

###  `pop`

**Signature**:
```python
def pop(self, key: Any, default=...) -> T | "Pile[T]" | None
```

**Parameters**:
- `key`: Key of item(s) to remove and return. Can be single key or collection of keys.
- `default`: Default value if key not found. If not specified and key not found, raises `ItemNotFoundError`.

**Return Values**:
- `T | Pile[T] | None`: Removed item(s) associated with key. Single items returned directly, multiple items in new `Pile`. Returns default if provided and key not found.

**Exceptions Raised**:
- `ItemNotFoundError`: If key not found and no default specified.

**Description**:
Removes and returns item(s) associated with a given key.

**Usage Examples**:
```python
# Example: Pop an item by index
item = pile_instance.pop(0)

# Example: Pop an item by LionID
item = pile_instance.pop("item_id")
```

###  `get`

**Signature**:
```python
def get(self, key: Any, default=...) -> T | "Pile[T]" | None
```

**Parameters**:
- `key`: Key of item(s) to retrieve. Can be single or collection.
- `default`: Default value if key not found. If not specified and key not found, raises `ItemNotFoundError`.

**Return Values**:
- `T | Pile[T] | None`: Retrieved item(s) associated with key. Single items returned directly, multiple items in new `Pile`. Returns default if provided and key not found.

**Exceptions Raised**:
- `ItemNotFoundError`: If key not found and no default specified.

**Description**:
Retrieves item(s) associated with a given key.

**Usage Examples**:
```python
# Example: Get an item by index
item = pile_instance.get(0)

# Example: Get an item by LionID
item = pile_instance.get("item_id")
```

###  `update`

**Signature**:
```python
def update(self, other: Any) -> None
```

**Parameters**:
- `other`: Collection to update with. Can be any LionIDable.

**Return Values**:
- `None`

**Description**:
Updates the pile with another collection of items.

**Usage Examples**:
```python
# Example: Update the pile with new items
pile_instance.update(new_items)
```

###  `clear`

**Signature**:
```python
def clear() -> None
```

**Return Values**:
- `None`

**Description**:
Clears all items, resetting the pile to an empty state.

**Usage Examples**:
```python
# Example: Clear the pile
pile_instance.clear()
```

###  `include`

**Signature**:
```python
def include(self, item: Any) -> bool
```

**Parameters**:
- `item`: Item(s) to include. Can be single item or collection.

**Return Values**:
- `bool`: True if the item(s) are in the pile after the operation, False otherwise.

**Description**:
Includes item(s) in the pile if not already present.

**Usage Examples**:
```python
# Example: Include an item in the pile
included = pile_instance.include("item_id")
print("Item included:", included)
```

###  `exclude`

**Signature**:
```python
def exclude(self, item: Any) -> bool
```

**Parameters**:
- `item`: Item(s) to exclude. Can be single item or collection.

**Return Values**:
- `bool`: True if the item(s) are not in the pile after the operation, False otherwise.

**Description**:
Excludes item(s) from the pile if present.

**Usage Examples**:
```python
# Example: Exclude an item from the pile
excluded = pile_instance.exclude("item_id")
print("Item excluded:", excluded)
```

###  `is_homogenous`

*also check [[Type Conversion Lib#^6aef9f|here]]

**Signature**:
```python
def is_homogenous() -> bool
```

**Return Values**:
- `bool`: True if all items have the same data type, False otherwise.

**Description**:
Checks if all items have the same data type.

**Usage Examples**:
```python
# Example: Check if the pile is homogenous
is_homogenous = pile_instance.is_homogenous()
print("Pile is homogenous:", is_homogenous)
```

###  `is_empty`

**Signature**:
```python
def is_empty() -> bool
```

**Return Values**:
- `bool`: True if the pile is empty, False otherwise.

**Description**:
Checks if the pile is empty.

**Usage Examples**:
```python
# Example: Check if the pile is empty
is_empty = pile_instance.is_empty()
print("Pile is empty:", is_empty)
```


###  `size`

**Signature**:
```python
def size() -> int
```

**Return Values**:
- `int`: The total size of the pile.

**Description**:
Returns the total size of the pile.

**Usage Examples**:
```python
# Example: Get the total size of the pile
total_size = pile_instance.size()
print("Total size of the pile:", total_size)
```

###  `insert`

**Signature**:
```python
def insert(self, index, item)
```

**Parameters**:
- `index`: Index to insert item(s). Must be integer.
- `item`: Item(s) to insert. Can be single item or collection.

**Exceptions Raised**:
- `ValueError`: If index not an integer.
- `IndexError`: If index out of range.

**Description**:
Inserts item(s) at specific position.

**Usage Examples**:
```python
# Example: Insert an item at a specific index
pile_instance.insert(0, new_item)
```

###  `append`

**Signature**:
```python
def append(self, item: T)
```

**Parameters**:
- `item`: Item to append. Can be any object, including `Pile`.

**Return Values**:
- `None`

**Description**:
Appends item to the end of the pile.

**Usage Examples**:
```python
# Example: Append an item to the pile
pile_instance.append(new_item)
```

###  `keys`

**Signature**:
```python
def keys() -> list[str]
```

**Return Values**:
- `list[str]`: The keys of the items in the pile.

**Description**:
Yields the keys of the items in the pile.

**Usage Examples**:
```python
# Example: Get the keys of the items in the pile
keys = pile_instance.keys()
print("Keys:", keys)
```

###  `values`

**Signature**:
```python
def values() -> Iterator[T]
```

**Return Values**:
- `Iterator[T]`: The values of the items in the pile.

**Description**:
Yields the values of the items in the pile.

**Usage Examples**:
```python
# Example: Get the values of the items in the pile
for value in pile_instance.values():
    print(value)
```

###  `items`

**Signature**:
```python
def items() -> Iterator[tuple[str, T]]
```

**Return Values**:
- `Iterator[tuple[str, T]]`: The items in the pile as (key, value) pairs.

**Description**:
Yields the items in the pile as (key, value) pairs.

**Usage Examples**:
```python
# Example: Get the items in the pile as (key, value) pairs
for key, value in pile_instance.items():
    print(key, value)
```

###  `to_df`

**Signature**:
```python
def to_df() -> DataFrame
```

**Return Values**:
- `DataFrame`: A DataFrame representation of the pile.

**Description**:
Converts the pile to a DataFrame.

**Usage Examples**:
```python
# Example: Convert the pile to a DataFrame
df = pile_instance.to_df()
print(df)
```

###  `create_index`

**Signature**:
```python
def create_index(self, index_type="llama_index", **kwargs)
```

**Parameters**:
- `index_type` (str): The type of index to use. Default is "llama_index".
- `**kwargs`: Additional keyword arguments for the index creation.

**Return Values**:
- The created index.

**Exceptions Raised**:
- `ValueError`: If an invalid index type is provided.

**Description**:
Creates an index for the pile.

**Usage Examples**:
```python
# Example: Create an index for the pile
index = pile_instance.create_index()
```

###  `create_query_engine`

**Signature**:
```python
def create_query_engine(self, index_type="llama_index", engine_kwargs={}, **kwargs)
```

**Parameters**:
- `index_type` (str): The type of index to use. Default is "llama_index".
- `engine_kwargs` (dict): Additional keyword arguments for the engine.
- `**kwargs`: Additional keyword arguments for the index creation.

**Exceptions Raised**:
- `ValueError`: If an invalid index type is provided.

**Description**:
Creates a query engine for the pile.

**Usage Examples**:
```python
# Example: Create a query engine for the pile
pile_instance.create_query_engine()
```

###  `create_chat_engine`

**Signature**:
```python
def create_chat_engine(self, index_type="llama_index", engine_kwargs={}, **kwargs)
```

**Parameters**:
- `index_type` (str): The type of index to use. Default is "llama_index".
- `engine_kwargs` (dict): Additional keyword arguments for the engine.
- `**kwargs`: Additional keyword arguments for the index creation.

**Exceptions Raised**:
- `ValueError`: If an invalid index type is provided.

**Description**:
Creates a chat engine for the pile.

**Usage Examples**:
```python
# Example: Create a chat engine for the pile
pile_instance.create_chat_engine()
```

###  `query_pile`

**Signature**:
```python
async def query_pile(self, query, engine_kwargs={}, **kwargs) -> str
```

**Parameters**:
- `query` (str): The query to send.
- `engine_kwargs` (dict): Additional keyword arguments for the engine.
- `**kwargs`: Additional keyword arguments for the query.

**Return Values**:
- `str`: The response from the query engine.

**Description**:
Queries the pile using the created query engine.

**Usage Examples**:
```python
# Example: Query the pile
response = await pile_instance.query_pile("query")
print(response)
```

###  `chat_pile`

**Signature**:
```python
async def chat_pile(self, query, engine_kwargs={}, **kwargs) -> str
```

**Parameters**:
- `query` (str): The query to send.
- `engine_kwargs` (dict): Additional keyword arguments for the engine.
- `**kwargs`: Additional keyword arguments for the query.

**Return Values**:
- `str`: The response from the chat engine.

**Description**

:
Chats with the pile using the created chat engine.

**Usage Examples**:
```python
# Example: Chat with the pile
response = await pile_instance.chat_pile("query")
print(response)
```

###  `embed_pile`

**Signature**:
```python
async def embed_pile(self, imodel=None, field="content", embed_kwargs={}, verbose=True, **kwargs)
```

**Parameters**:
- `imodel`: The embedding model to use.
- `field` (str): The field to embed. Default is "content".
- `embed_kwargs` (dict): Additional keyword arguments for the embedding.
- `verbose` (bool): Whether to print verbose messages. Default is True.
- `**kwargs`: Additional keyword arguments for the embedding.

**Exceptions Raised**:
- `ModelLimitExceededError`: If the model limit is exceeded.

**Description**:
Embeds the items in the pile.

**Usage Examples**:
```python
# Example: Embed the items in the pile
await pile_instance.embed_pile(imodel=my_model)
```

###  `to_csv`

**Signature**:
```python
def to_csv(self, file_name, **kwargs) -> None
```

**Parameters**:
- `file_name` (str): The name of the CSV file.
- `**kwargs`: Additional keyword arguments for the CSV writer.

**Return Values**:
- `None`

**Description**:
Saves the pile to a CSV file.

**Usage Examples**:
```python
# Example: Save the pile to a CSV file
pile_instance.to_csv("pile.csv")
```

###  `from_csv`

**Signature**:
```python
@classmethod
def from_csv(cls, file_name, **kwargs) -> "Pile"
```

**Parameters**:
- `file_name` (str): The name of the CSV file.
- `**kwargs`: Additional keyword arguments for the CSV reader.

**Return Values**:
- `Pile`: The loaded pile.

**Description**:
Loads a pile from a CSV file.

**Usage Examples**:
```python
# Example: Load a pile from a CSV file
pile_instance = Pile.from_csv("pile.csv")
```

###  `from_df`

**Signature**:
```python
@classmethod
def from_df(cls, df) -> "Pile"
```

**Parameters**:
- `df` (DataFrame): The DataFrame to load.

**Return Values**:
- `Pile`: The loaded pile.

**Description**:
Loads a pile from a DataFrame.

**Usage Examples**:
```python
# Example: Load a pile from a DataFrame
pile_instance = Pile.from_df(df)
```

###  `as_query_tool`

**Signature**:
```python
def as_query_tool(self, index_type="llama_index", query_type="query", name=None, guidance=None, query_description=None, **kwargs)
```

**Parameters**:
- `index_type` (str): The type of index to use. Default is "llama_index".
- `query_type` (str): The type of query engine to use. Default is "query".
- `name` (str): The name of the query tool. Default is "query".
- `guidance` (str): The guidance for the query tool.
- `query_description` (str): The description of the query parameter.
- `**kwargs`: Additional keyword arguments for the query engine.

**Return Values**:
- `Tool`: The created query tool.

**Description**:
Creates a query tool for the pile.

**Usage Examples**:
```python
# Example: Create a query tool for the pile
query_tool = pile_instance.as_query_tool()
```



###  `__iter__`

**Signature**:
```python
def __iter__() -> Iterator[T]
```

**Return Values**:
- `Iterator[T]`: An iterator over the items in the pile.

**Description**:
Returns an iterator over the items in the pile.

**Usage Examples**:
```python
# Example: Iterate over the items in the pile
for item in pile_instance:
    print(item)
```

###  `__len__`

**Signature**:
```python
def __len__() -> int
```

**Return Values**:
- `int`: The number of items in the

 pile.

**Description**:
Returns the number of items in the pile.

**Usage Examples**:
```python
# Example: Get the number of items in the pile
length = len(pile_instance)
print("Number of items:", length)
```

###  `__add__`

**Signature**:
```python
def __add__(self, other: T) -> "Pile"
```

**Parameters**:
- `other`: Item(s) to include. Can be single item or collection.

**Return Values**:
- `Pile`: New `Pile` with all items from current pile plus item(s).

**Exceptions Raised**:
- `LionValueError`: If item(s) can't be included.

**Description**:
Creates a new pile by including item(s) using `+`.

**Usage Examples**:
```python
# Example: Add items to the pile
new_pile = pile_instance + new_item
```

###  `__sub__`

**Signature**:
```python
def __sub__(self, other) -> "Pile"
```

**Parameters**:
- `other`: Item(s) to exclude. Can be single item or collection.

**Return Values**:
- `Pile`: New `Pile` with all items from current pile except item(s).

**Exceptions Raised**:
- `ItemNotFoundError`: If item(s) not found in pile.

**Description**:
Creates a new pile by excluding item(s) using `-`.

**Usage Examples**:
```python
# Example: Subtract items from the pile
new_pile = pile_instance - item_to_remove
```

###  `__iadd__`

**Signature**:
```python
def __iadd__(self, other: T) -> "Pile"
```

**Parameters**:
- `other`: Item(s) to include. Can be single item or collection.

**Return Values**:
- `Pile`: Modified pile after including item(s).

**Description**:
Includes item(s) in the current pile in place using `+=`.

**Usage Examples**:
```python
# Example: Add items to the pile in place
pile_instance += new_item
```

###  `__isub__`

**Signature**:
```python
def __isub__(self, other: LionIDable) -> "Pile"
```

**Parameters**:
- `other`: Item(s) to exclude. Can be single item or collection.

**Return Values**:
- `Pile`: Modified pile after excluding item(s).

**Description**:
Excludes item(s) from the current pile in place using `-=`.

**Usage Examples**:
```python
# Example: Subtract items from the pile in place
pile_instance -= item_to_remove
```

###  `__radd__`

**Signature**:
```python
def __radd__(self, other: T) -> "Pile"
```

**Parameters**:
- `other`: Item(s) to include. Can be single item or collection.

**Return Values**:
- `Pile`: New `Pile` with all items from current pile plus item(s).

**Description**:
Supports right addition for items to the pile.

**Usage Examples**:
```python
# Example: Right add items to the pile
new_pile = new_item + pile_instance
```


###  `__list__`

**Signature**:
```python
def __list__() -> list
```

**Return Values**:
- `list`: The items in the pile.

**Description**:
Gets a list of the items in the pile.

**Usage Examples**:
```python
# Example: Get a list of the items in the pile
items_list = pile_instance.__list__()
print(items_list)
```

###  `__str__`

**Signature**:
```python
def __str__() -> str
```

**Return Values**:
- `str`: The string representation of the pile.

**Description**:
Gets the string representation of the pile.

**Usage Examples**:
```python
# Example: Get the string representation of the pile
print(str(pile_instance))
```

###  `__repr__`

**Signature**:
```python
def __repr__() -> str
```

**Return Values**:
- `str`: The representation of the pile.

**Description**:
Gets the representation of the pile.

**Usage Examples**:
```python
# Example: Get the representation of the pile
print(repr(pile_instance))
```

## Function: `pile`

**Signature**:
```python
def pile(items: Iterable[T] | None = None, item_type: set[Type] | None = None, order=None, use_obj=None, csv_file=None, df=None, **kwargs) -> Pile[T]
```

**Description**:
Creates a new `Pile` instance. This function provides various ways to create a `Pile` instance, including from items, a CSV file, or a DataFrame.

**Parameters**:
- `items` (Iterable[T] | None): The items to include in the pile.
- `item_type` (set[Type] | None): The allowed types of items in the pile.
- `order` (list[str] | None): The order of items.
- `use_obj` (bool | None): Whether to treat `Record` and `Ordering` as objects.
- `csv_file` (str | None): The path to a CSV file to load items from.
- `df` (DataFrame | None): A DataFrame to load items from.
- `**kwargs`: Additional keyword arguments for loading from CSV or DataFrame.

**Return Values**:
- `Pile[T]`: A new `Pile` instance.

**Exceptions Raised**:
- `ValueError`: If invalid arguments are provided.

**Usage Examples**:
```python
# Example: Create a new Pile instance from items
pile_instance = pile(items=my_items)

# Example: Create a new Pile instance from a CSV file
pile_instance = pile(csv_file="pile.csv")

# Example: Create a new Pile instance from a DataFrame
pile_instance = pile(df=my_dataframe)
```
