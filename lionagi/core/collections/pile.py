from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable, Iterable
from functools import wraps
from typing import Any, Generic, TypeVar

from pydantic import Field, field_validator

from lionagi.libs.ln_convert import is_same_dtype, to_df, to_dict
from lionagi.libs.ln_func_call import CallDecorator as cd
from lionagi.libs.ln_func_call import alcall

from .abc import (
    Component,
    Element,
    ItemNotFoundError,
    LionIDable,
    LionTypeError,
    LionValueError,
    ModelLimitExceededError,
    Ordering,
    Record,
    get_lion_id,
)
from .model import iModel
from .util import _validate_order, to_list_type

T = TypeVar("T")


def async_synchronized(func: Callable):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self.async_lock:
            return await func(self, *args, **kwargs)

    return wrapper


class Pile(Element, Record, Generic[T]):
    """
    Collection class for managing Element objects.

    Facilitates ordered and type-validated storage and access, supporting
    both index-based and key-based retrieval.

    Attributes:
        pile (dict[str, T]): Maps unique identifiers to items.
        item_type (set[Type[Element]] | None): Allowed item types.
        name (str | None): Optional name for the pile.
        order (list[str]): Order of item identifiers.
        use_obj (bool): If True, treat Record and Ordering as objects.
    """

    use_obj: bool = False
    pile: dict[str, T] = Field(default_factory=dict)
    item_type: set[type[Element]] | None = Field(default=None)
    name: str | None = None
    order: list[str] = Field(default_factory=list)
    index: Any = None
    engines: dict[str, Any] = Field(default_factory=dict)
    query_response: list = []
    tools: dict = {}

    def __pydantic_extra__(self) -> dict[str, Any]:
        return {
            "_async": Field(default_factory=asyncio.Lock),
        }

    def __pydantic_private__(self) -> dict[str, Any]:
        return self.__pydantic_extra__()

    def __init__(
        self,
        items=None,
        item_type=None,
        order=None,
        use_obj=None,
    ):
        super().__init__()

        self.use_obj = use_obj or False
        self.pile = self._validate_pile(items or {})
        self.item_type = self._validate_item_type(item_type)

        order = order or list(self.pile.keys())
        if not len(order) == len(self):
            raise ValueError(
                "The length of the order does not match the length of the pile"
            )
        self.order = order

    def __getitem__(self, key) -> T | Pile[T]:
        """
        Retrieve items from the pile using a key.

        Supports multiple types of key access:
        - By index or slice (list-like access)
        - By LionID (dictionary-like access)
        - By other complex types if item is of LionIDable

        Args:
            key: Key to retrieve items.

        Returns:
            The requested item(s). Single items returned directly,
            multiple items returned in a new `Pile` instance.

        Raises:
            ItemNotFoundError: If requested item(s) not found.
            LionTypeError: If provided key is invalid.
        """
        try:
            if isinstance(key, (int, slice)):
                # Handle list-like index or slice
                _key = self.order[key]
                _key = [_key] if isinstance(key, int) else _key
                _out = [self.pile.get(i) for i in _key]
                return (
                    _out[0]
                    if len(_out) == 1
                    else pile(_out, self.item_type, _key)
                )
        except IndexError as e:
            raise ItemNotFoundError(key) from e

        keys = to_list_type(key)
        for idx, item in enumerate(keys):
            if isinstance(item, str):
                keys[idx] = item
                continue
            if hasattr(item, "ln_id"):
                keys[idx] = item.ln_id

        if not all(keys):
            raise LionTypeError(
                "Invalid item type. Expected LionIDable object(s)."
            )

        try:
            if len(keys) == 1:
                return self.pile.get(keys[0])
            return pile([self.pile.get(i) for i in keys], self.item_type, keys)
        except KeyError as e:
            raise ItemNotFoundError(key) from e

    def __setitem__(self, key, item) -> None:
        """
        Set new values in the pile using various key types.

        Handles single/multiple assignments, ensures type consistency.
        Supports index/slice, LionID, and LionIDable key access.

        Args:
            key: Key to set items. Can be index, slice, LionID, LionIDable.
            item: Item(s) to set. Can be single item or collection.

        Raises:
            ValueError: Length mismatch or multiple items to single key.
            LionTypeError: Item type doesn't match allowed types.
        """
        item = self._validate_pile(item)

        if isinstance(key, (int, slice)):
            # Handle list-like index or slice
            try:
                _key = self.order[key]
            except IndexError as e:
                raise e

            if isinstance(_key, str) and len(item) != 1:
                raise ValueError(
                    "Cannot assign multiple items to a single item."
                )

            if isinstance(_key, list) and len(item) != len(_key):
                raise ValueError(
                    "The length of values does not match the length of the slice"
                )

            for k, v in item.items():
                if self.item_type and type(v) not in self.item_type:
                    raise LionTypeError(
                        f"Invalid item type. Expected {self.item_type}"
                    )

                self.pile[k] = v
                self.order[key] = k
                self.pile.pop(_key)
            return

        if len(to_list_type(key)) != len(item):
            raise ValueError(
                "The length of keys does not match the length of values"
            )

        self.pile.update(item)
        self.order.extend(item.keys())

    def __contains__(self, item: Any) -> bool:
        """
        Check if item(s) are present in the pile.

        Accepts individual items and collections. Returns `True` if all
        provided items are found, `False` otherwise.

        Args:
            item: Item(s) to check. Can be single item or collection.

        Returns:
            `True` if all items are found, `False` otherwise.
        """
        item = to_list_type(item)
        for i in item:
            try:
                a = i if isinstance(i, str) else get_lion_id(i)
                if a not in self.pile:
                    return False
            except Exception:
                return False

        return True

    def pop(self, key: Any, default=...) -> T | Pile[T] | None:
        """
        Remove and return item(s) associated with given key.

        Raises `ItemNotFoundError` if key not found and no default given.
        Returns default if provided and key not found.

        Args:
            key: Key of item(s) to remove and return. Can be single key
                or collection of keys.
            default: Default value if key not found. If not specified
                and key not found, raises `ItemNotFoundError`.

        Returns:
            Removed item(s) associated with key. Single items returned
            directly, multiple items in new `Pile`. Returns default if
            provided and key not found.

        Raises:
            ItemNotFoundError: If key not found and no default specified.
        """
        key = to_list_type(key)
        items = []

        for i in key:
            if i not in self:
                if default == ...:
                    raise ItemNotFoundError(i)
                return default

        for i in key:
            _id = get_lion_id(i)
            items.append(self.pile.pop(_id))
            self.order.remove(_id)

        return pile(items) if len(items) > 1 else items[0]

    def get(self, key: Any, default=...) -> T | Pile[T] | None:
        """
        Retrieve item(s) associated with given key.

        Raises `ItemNotFoundError` if key not found and no default given.
        Returns default if provided and key not found.

        Args:
            key: Key of item(s) to retrieve. Can be single or collection.
            default: Default value if key not found. If not specified
                and key not found, raises `ItemNotFoundError`.

        Returns:
            Retrieved item(s) associated with key. Single items returned
            directly, multiple items in new `Pile`. Returns default if
            provided and key not found.

        Raises:
            ItemNotFoundError: If key not found and no default specified.
        """
        try:
            return self[key]
        except ItemNotFoundError as e:
            if default == ...:
                raise e
            return default

    def update(self, other: Any):
        """
        Update pile with another collection of items.

        Accepts `Pile` or any iterable. Provided items added to current
        pile, overwriting existing items with same keys.

        Args:
            other: Collection to update with. Can be any LionIDable
        """
        p = pile(other)
        self[p] = p

    def clear(self):
        """Clear all items, resetting pile to empty state."""
        self.pile.clear()
        self.order.clear()

    def include(self, item: Any) -> bool:
        """
        Include item(s) in pile if not already present.

        Accepts individual items and collections. Adds items if not
        present. Returns `True` if item(s) in pile after operation,
        `False` otherwise.

        Args:
            item: Item(s) to include. Can be single item or collection.

        Returns:
            `True` if item(s) in pile after operation, `False` otherwise.
        """
        item = to_list_type(item)
        if item not in self:
            self[item] = item
        return item in self

    def exclude(self, item: Any) -> bool:
        """
        Exclude item(s) from pile if present.

        Accepts individual items and collections. Removes items if
        present. Returns `True` if item(s) not in pile after operation,
        `False` otherwise.

        Args:
            item: Item(s) to exclude. Can be single item or collection.

        Returns:
            `True` if item(s) not in pile after operation, `False` else.
        """
        item = to_list_type(item)
        for i in item:
            if item in self:
                self.pop(i)
        return item not in self

    def is_homogenous(self) -> bool:
        """
        Check if all items have the same data type.

        Returns:
            `True` if all items have the same type, `False` otherwise.
            Empty pile or single-item pile considered homogenous.
        """
        return len(self.pile) < 2 or all(is_same_dtype(self.pile.values()))

    def is_empty(self) -> bool:
        """
        Check if the pile is empty.

        Returns:
            bool: `True` if the pile is empty, `False` otherwise.
        """
        return not self.pile

    def __iter__(self):
        """Return an iterator over the items in the pile.

        Yields:
            The items in the pile in the order they were added.
        """
        return iter(self.values())

    def __len__(self) -> int:
        """Get the number of items in the pile.

        Returns:
            int: The number of items in the pile.
        """
        return len(self.pile)

    def __add__(self, other: T) -> Pile:
        """Create a new pile by including item(s) using `+`.

        Returns a new `Pile` with all items from the current pile plus
        provided item(s). Raises `LionValueError` if item(s) can't be
        included.

        Args:
            other: Item(s) to include. Can be single item or collection.

        Returns:
            New `Pile` with all items from current pile plus item(s).

        Raises:
            LionValueError: If item(s) can't be included.
        """
        _copy = self.model_copy(deep=True)
        if _copy.include(other):
            return _copy
        raise LionValueError("Item cannot be included in the pile.")

    def __sub__(self, other) -> Pile:
        """
        Create a new pile by excluding item(s) using `-`.

        Returns a new `Pile` with all items from the current pile except
        provided item(s). Raises `ItemNotFoundError` if item(s) not found.

        Args:
            other: Item(s) to exclude. Can be single item or collection.

        Returns:
            New `Pile` with all items from current pile except item(s).

        Raises:
            ItemNotFoundError: If item(s) not found in pile.
        """
        _copy = self.model_copy(deep=True)
        if other not in self:
            raise ItemNotFoundError(other)

        length = len(_copy)
        if not _copy.exclude(other) or len(_copy) == length:
            raise LionValueError("Item cannot be excluded from the pile.")
        return _copy

    def __iadd__(self, other: T) -> Pile:
        """
        Include item(s) in the current pile in place using `+=`.

        Modifies the current pile in-place by including item(s). Returns
        the modified pile.

        Args:
            other: Item(s) to include. Can be single item or collection.
        """

        return self + other

    def __isub__(self, other: LionIDable) -> Pile:
        """
        Exclude item(s) from the current pile using `-=`.

        Modifies the current pile in-place by excluding item(s). Returns
        the modified pile.

        Args:
            other: Item(s) to exclude. Can be single item or collection.

        Returns:
            Modified pile after excluding item(s).
        """
        return self - other

    def __radd__(self, other: T) -> Pile:
        return other + self

    def __ior__(self, other: Any | Pile) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )
        other = self._validate_pile(list(other))
        self.include(other)
        return self

    def __or__(self, other: Any | Pile) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )

        result = self.__class__(
            items=self.values(),
            item_type=self.item_type,
            order=self.order,
        )
        result.include(list(other))
        return result

    def __ixor__(self, other: Any | Pile) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )

        to_exclude = []
        for i in other:
            if i in self:
                to_exclude.append(i)

        other = [i for i in other if i not in to_exclude]
        self.exclude(to_exclude)
        self.include(other)
        return self

    def __xor__(self, other: Any | Pile) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )

        to_exclude = []
        for i in other:
            if i in self:
                to_exclude.append(i)

        values = [i for i in self if i not in to_exclude] + [
            i for i in other if i not in to_exclude
        ]

        result = self.__class__(
            items=values,
            item_type=self.item_type,
        )
        return result

    def __iand__(self, other: Any) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )

        to_exclude = []
        for i in self.values():
            if i not in other:
                to_exclude.append(i)
        self.exclude(to_exclude)
        return self

    def __and__(self, other: Any | Pile) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )

        values = [i for i in self if i in other]
        return self.__class__(
            items=values,
            item_type=self.item_type,
        )

    def size(self) -> int:
        """Return the total size of the pile."""
        return sum([len(i) for i in self])

    def insert(self, index, item):
        """
        Insert item(s) at specific position.

        Inserts item(s) at specified index. Index must be integer.
        Raises `IndexError` if index out of range.

        Args:
            index: Index to insert item(s). Must be integer.
            item: Item(s) to insert. Can be single item or collection.

        Raises:
            ValueError: If index not an integer.
            IndexError: If index out of range.
        """
        if not isinstance(index, int):
            raise ValueError("Index must be an integer for pile insertion.")
        item = self._validate_pile(item)
        for k, v in item.items():
            self.order.insert(index, k)
            self.pile[k] = v

    def append(self, item: T):
        """
        Append item to end of pile.

        Appends item to end of pile. If item is `Pile`, added as single
        item, preserving structure. Only way to add `Pile` into another.
        Other methods assume pile as container only.

        Args:
            item: Item to append. Can be any object, including `Pile`.
        """
        self.pile[item.ln_id] = item
        self.order.append(item.ln_id)

    def keys(self):
        """Yield the keys of the items in the pile."""
        return self.order

    def values(self):
        """Yield the values of the items in the pile."""
        yield from (self.pile.get(i) for i in self.order)

    def items(self):
        """
        Yield the items in the pile as (key, value) pairs.

        Yields:
            tuple: A tuple containing the key and value of each item in the pile.
        """
        yield from ((i, self.pile.get(i)) for i in self.order)

    @field_validator("order", mode="before")
    def _validate_order(cls, value):
        return _validate_order(value)

    def _validate_item_type(self, value):
        """
        Validate the item type for the pile.

        Ensures that the provided item type is a subclass of Element or iModel.
        Raises an error if the validation fails.

        Args:
            value: The item type to validate. Can be a single type or a list of types.

        Returns:
            set: A set of validated item types.

        Raises:
            LionTypeError: If an invalid item type is provided.
            LionValueError: If duplicate item types are detected.
        """
        if value is None:
            return None

        value = to_list_type(value)

        for i in value:
            if not isinstance(i, (type(Element), type(iModel))):
                raise LionTypeError(
                    "Invalid item type. Expected a subclass of Component."
                )

        if len(value) != len(set(value)):
            raise LionValueError(
                "Detected duplicated item types in item_type."
            )

        if len(value) > 0:
            return set(value)

    def _validate_pile(
        self,
        value,
    ):
        if value == {}:
            return value

        if isinstance(value, Component):
            return {value.ln_id: value}

        if self.use_obj:
            if not isinstance(value, list):
                value = [value]
            if isinstance(value[0], (Record, Ordering)):
                return {getattr(i, "ln_id"): i for i in value}

        value = to_list_type(value)
        if getattr(self, "item_type", None) is not None:
            for i in value:
                if not type(i) in self.item_type:
                    raise LionTypeError(
                        f"Invalid item type in pile. Expected {self.item_type}"
                    )

        if isinstance(value, list):
            if len(value) == 1:
                if isinstance(value[0], dict) and value[0] != {}:
                    k = list(value[0].keys())[0]
                    v = value[0][k]
                    return {k: v}

                # [item]
                k = getattr(value[0], "ln_id", None)
                if k:
                    return {k: value[0]}

            return {i.ln_id: i for i in value}

        raise LionValueError("Invalid pile value")

    def to_df(self):
        """Return the pile as a DataFrame."""
        dicts_ = []
        for i in self.values():
            _dict = i.to_dict()
            if _dict.get("embedding", None):
                _dict["embedding"] = str(_dict.get("embedding"))
            dicts_.append(_dict)
        return to_df(dicts_)

    def create_index(self, index_type="llama_index", **kwargs):
        """
        Create an index for the pile.

        Args:
            index_type (str): The type of index to use. Default is "llama_index".
            **kwargs: Additional keyword arguments for the index creation.

        Returns:
            The created index.

        Raises:
            ValueError: If an invalid index type is provided.
        """
        if index_type == "llama_index":
            from lionagi.integrations.bridge import LlamaIndexBridge

            index_nodes = None

            try:
                index_nodes = [i.to_llama_index_node() for i in self]
            except AttributeError:
                raise LionTypeError(
                    "Invalid item type. Expected a subclass of Component."
                )

            self.index = LlamaIndexBridge.index(index_nodes, **kwargs)
            return self.index

        raise ValueError("Invalid index type")

    def create_query_engine(
        self, index_type="llama_index", engine_kwargs={}, **kwargs
    ):
        """
        Create a query engine for the pile.

        Args:
            index_type (str): The type of index to use. Default is "llama_index".
            engine_kwargs (dict): Additional keyword arguments for the engine.
            **kwargs: Additional keyword arguments for the index creation.

        Raises:
            ValueError: If an invalid index type is provided.
        """
        if index_type == "llama_index":
            if "node_postprocessor" in kwargs:
                engine_kwargs["node_postprocessor"] = kwargs.pop(
                    "node_postprocessor"
                )
            if "llm" in kwargs:
                engine_kwargs["llm"] = kwargs.pop("llm")
            if not self.index:
                self.create_index(index_type, **kwargs)
            query_engine = self.index.as_query_engine(**engine_kwargs)
            self.engines["query"] = query_engine
        else:
            raise ValueError("Invalid index type")

    def create_chat_engine(
        self, index_type="llama_index", engine_kwargs={}, **kwargs
    ):
        """
        Create a chat engine for the pile.

        Args:
            index_type (str): The type of index to use. Default is "llama_index".
            engine_kwargs (dict): Additional keyword arguments for the engine.
            **kwargs: Additional keyword arguments for the index creation.

        Raises:
            ValueError: If an invalid index type is provided.
        """
        if index_type == "llama_index":
            if "node_postprocessor" in kwargs:
                engine_kwargs["node_postprocessor"] = kwargs.pop(
                    "node_postprocessor"
                )
            if "llm" in kwargs:
                engine_kwargs["llm"] = kwargs.pop("llm")
            if not self.index:
                self.create_index(index_type, **kwargs)
            query_engine = self.index.as_chat_engine(**engine_kwargs)
            self.engines["chat"] = query_engine
        else:
            raise ValueError("Invalid index type")

    async def query_pile(
        self, query, engine_kwargs={}, return_dict=False, **kwargs
    ):
        """
        Query the pile using the created query engine.

        Args:
            query (str): The query to send.
            engine_kwargs (dict): Additional keyword arguments for the engine.
            **kwargs: Additional keyword arguments for the query.

        Returns:
            str: The response from the query engine.
        """
        if not self.engines.get("query", None):
            self.create_query_engine(**engine_kwargs)
        response = await self.engines["query"].aquery(query, **kwargs)
        self.query_response.append(response)
        if return_dict:
            return to_dict(response)
        return str(response)

    async def chat_pile(
        self, query, engine_kwargs={}, return_dict=False, **kwargs
    ):
        """
        Chat with the pile using the created chat engine.

        Args:
            query (str): The query to send.
            engine_kwargs (dict): Additional keyword arguments for the engine.
            **kwargs: Additional keyword arguments for the query.

        Returns:
            str: The response from the chat engine.
        """
        if not self.engines.get("chat", None):
            self.create_chat_engine(**engine_kwargs)
        response = await self.engines["chat"].achat(query, **kwargs)
        self.query_response.append(response)
        if return_dict:
            return to_dict(response)
        return str(response)

    async def embed_pile(
        self,
        imodel=None,
        field="content",
        embed_kwargs={},
        verbose=True,
        **kwargs,
    ):
        """
        Embed the items in the pile.

        Args:
            imodel: The embedding model to use.
            field (str): The field to embed. Default is "content".
            embed_kwargs (dict): Additional keyword arguments for the embedding.
            verbose (bool): Whether to print verbose messages. Default is True.
            **kwargs: Additional keyword arguments for the embedding.

        Raises:
            ModelLimitExceededError: If the model limit is exceeded.
        """
        from .model import iModel

        imodel = imodel or iModel(endpoint="embeddings", **kwargs)

        max_concurrency = kwargs.get("max_concurrency", None) or 100

        @cd.max_concurrency(max_concurrency)
        async def _embed_item(item):
            try:
                return await imodel.embed_node(
                    item, field=field, **embed_kwargs
                )
            except ModelLimitExceededError:
                pass
            return None

        await alcall(list(self), _embed_item)

        a = len([i for i in self if "embedding" in i._all_fields])
        if len(self) > a and verbose:
            print(
                f"Successfully embedded {a}/{len(self)} items, Failed to embed {len(self) - a}/{len(self)} items"
            )
            return

        print(f"Successfully embedded all {a}/{a} items")

    def to_csv(self, file_name, **kwargs):
        """
        Save the pile to a CSV file.

        Args:
            file_name (str): The name of the CSV file.
            **kwargs: Additional keyword arguments for the CSV writer.
        """
        self.to_df().to_csv(file_name, index=False, **kwargs)

    @classmethod
    def from_csv(cls, file_name, **kwargs):
        """
        Load a pile from a CSV file.

        Args:
            file_name (str): The name of the CSV file.
            **kwargs: Additional keyword arguments for the CSV reader.

        Returns:
            Pile: The loaded pile.
        """
        from pandas import read_csv

        df = read_csv(file_name, **kwargs)
        items = Component.from_obj(df)
        return cls(items)

    @classmethod
    def from_df(cls, df):
        """
        Load a pile from a DataFrame.

        Args:
            df (DataFrame): The DataFrame to load.

        Returns:
            Pile: The loaded pile.
        """
        items = Component.from_obj(df)
        return cls(items)

    def as_query_tool(
        self,
        index_type="llama_index",
        query_type="query",
        name=None,
        guidance=None,
        query_description=None,
        return_dict=False,
        **kwargs,
    ):
        """
        Create a query tool for the pile.

        Args:
            index_type (str): The type of index to use. Default is "llama_index".
            query_type (str): The type of query engine to use. Default is "query".
            name (str): The name of the query tool. Default is "query".
            guidance (str): The guidance for the query tool.
            query_description (str): The description of the query parameter.
            **kwargs: Additional keyword arguments for the query engine.

        Returns:
            Tool: The created query tool.
        """
        if not self.engines.get(query_type, None):
            if query_type == "query":
                self.create_query_engine(index_type=index_type, **kwargs)
            elif query_type == "chat":
                self.create_chat_engine(index_type=index_type, **kwargs)

        from lionagi.core.action.tool_manager import func_to_tool

        if not guidance:
            if query_type == "query":
                guidance = "Query a QA bot"
            elif query_type == "chat":
                guidance = "Chat with a QA bot"

        if not query_description:
            if query_type == "query":
                query_description = "The query to send"
            elif query_type == "chat":
                query_description = "The message to send"

        async def query(query: str):
            if query_type == "query":
                return await self.query_pile(
                    query, return_dict=return_dict, **kwargs
                )

            elif query_type == "chat":
                return await self.chat_pile(
                    query, return_dict=return_dict, **kwargs
                )

        name = name or "query"
        tool = func_to_tool(query)[0]
        tool.schema_["function"]["name"] = name
        tool.schema_["function"]["description"] = guidance
        tool.schema_["function"]["parameters"]["properties"]["query"][
            "description"
        ] = query_description
        self.tools[query_type] = tool
        return self.tools[query_type]

    def __list__(self):
        """
        Get a list of the items in the pile.

        Returns:
            list: The items in the pile.
        """
        return list(self.pile.values())

    def __str__(self):
        """
        Get the string representation of the pile.

        Returns:
            str: The string representation of the pile.
        """
        return self.to_df().__str__()

    def __repr__(self):
        """
        Get the representation of the pile.

        Returns:
            str: The representation of the pile.
        """
        return self.to_df().__repr__()

    def __getstate__(self):
        """Prepare the Pile instance for pickling."""
        state = self.__dict__.copy()
        state["_async_lock"] = None
        return state

    def __setstate__(self, state):
        """Restore the Pile instance after unpickling."""
        self.__dict__.update(state)
        self._async_lock = asyncio.Lock()

    @property
    def async_lock(self):
        """Ensure the async lock is always available, even during unpickling"""
        if not hasattr(self, "_async_lock") or self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock

    # Async Interface methods
    @async_synchronized
    async def asetitem(
        self,
        key: Any,
        item: T | Iterable[T],
        /,
    ) -> None:
        """Asynchronously set an item or items in the Pile.

        Args:
            key: The key to set. Can be an integer index, a string ID, or a
                slice.
            item: The item or items to set. Must be of type T or an iterable
                of T for slices.

        Raises:
            TypeError: If the item type is not allowed.
            KeyError: If the key is invalid.
            ValueError: If trying to set multiple items with a non-slice key.
        """
        self._setitem(key, item)

    @async_synchronized
    async def apop(
        self,
        key: Any,
        default: Any = ...,
        /,
    ):
        """Asynchronously remove and return an item or items from the Pile.

        Args:
            key: The key of the item(s) to remove. Can be an integer index,
                a string ID, or a slice.
            default: The value to return if the key is not found. Defaults to
                ....

        Returns:
            The removed item(s), or the default value if not found.

        Raises:
            KeyError: If the key is not found and no default is provided.
        """
        return self._pop(key, default)

    @async_synchronized
    async def aremove(
        self,
        item: T,
        /,
    ) -> None:
        """Asynchronously remove a specific item from the Pile.

        Args:
            item: The item to remove.

        Raises:
            ValueError: If the item is not found in the Pile.
        """
        self._remove(item)

    @async_synchronized
    async def ainclude(
        self,
        item: T | Iterable[T],
        /,
    ) -> None:
        """Asynchronously include item(s) in the Pile if not already present.

        Args:
            item: Item or iterable of items to include.

        Raises:
            TypeError: If the item(s) are not of allowed types.
        """
        self._include(item)
        if item not in self:
            raise LionTypeError(f"Item {item} is not of allowed types")

    @async_synchronized
    async def aexclude(
        self,
        item: T | Iterable[T],
        /,
    ) -> None:
        """Asynchronously exclude item(s) from the Pile if present.

        Args:
            item: Item or iterable of items to exclude.

        Note:
            This method does not raise an error if an item is not found.
        """
        self._exclude(item)

    @async_synchronized
    async def aclear(self) -> None:
        self._clear()

    @async_synchronized
    async def aupdate(
        self,
        other: Any,
        /,
    ) -> None:
        self._update(other)

    @async_synchronized
    async def aget(
        self,
        key: Any,
        default=...,
        /,
    ) -> list | Any | T:
        return self._get(key, default)

    async def __aiter__(self) -> AsyncIterator[T]:
        """Return an asynchronous iterator over the items in the Pile.

        This method creates a snapshot of the current order to prevent
        issues with concurrent modifications during iteration.

        Yields:
            Items in the Pile in their current order.

        Note:
            This method yields control to the event loop after each item,
            allowing other async operations to run between iterations.
        """

        async with self.async_lock:
            current_order = list(self.order)

        for key in current_order:
            yield self.pile_[key]
            await asyncio.sleep(0)  # Yield control to the event loop

    async def __anext__(self) -> T:
        """Asynchronously return the next item in the Pile."""
        try:
            return await anext(self.AsyncPileIterator(self))
        except StopAsyncIteration:
            raise StopAsyncIteration("End of pile")

    class AsyncPileIterator:
        def __init__(self, pile: Pile):
            self.pile = pile
            self.index = 0

        def __aiter__(self) -> AsyncIterator[T]:
            return self

        async def __anext__(self) -> T:
            if self.index >= len(self.pile):
                raise StopAsyncIteration
            item = self.pile[self.pile.order[self.index]]
            self.index += 1
            await asyncio.sleep(0)  # Yield control to the event loop
            return item


def pile(
    items: Iterable[T] | None = None,
    item_type: set[type] | None = None,
    order=None,
    use_obj=None,
    csv_file=None,
    df=None,
    **kwargs,
) -> Pile[T]:
    """
    Create a new Pile instance.

    This function provides various ways to create a Pile instance:
    - Directly from items
    - From a CSV file
    - From a DataFrame

    Args:
        items (Iterable[T] | None): The items to include in the pile.
        item_type (set[Type] | None): The allowed types of items in the pile.
        order (list[str] | None): The order of items.
        use_obj (bool | None): Whether to treat Record and Ordering as objects.
        csv_file (str | None): The path to a CSV file to load items from.
        df (DataFrame | None): A DataFrame to load items from.
        **kwargs: Additional keyword arguments for loading from CSV or DataFrame.

    Returns:
        Pile[T]: A new Pile instance.

    Raises:
        ValueError: If invalid arguments are provided.
    """
    if csv_file:
        return Pile.from_csv(csv_file, **kwargs)
    if df:
        return Pile.from_df(df)

    return Pile(items, item_type, order, use_obj)
