.. _lionagi_protocols_generic_pile:

=============================================================
Pile
=============================================================
.. module:: lionagi.protocols.generic.pile
   :synopsis: Provides an extensible collection class with concurrency support, 
              type enforcement, and adapter-based conversions.

Overview
--------
The :class:`Pile` class is a **thread-safe**, **async-compatible** collection 
of items. It merges the capabilities of an ordered container with concurrency 
locks and optional **type constraints**. Piles are well-suited for multi-threaded 
or async environments, where items must be inserted, retrieved, or removed 
safely. They also integrate with adapter-based conversions (like JSON, CSV, 
Excel, or DataFrames) for convenient data import/export.


Pile
----
.. class:: Pile(Element, Collective[E], Generic[E])
   :module: lionagi.protocols.generic.pile

   **Inherits from**: :class:`~lionagi.protocols.generic.element.Element`, :class:`~lionagi.protocols._concepts.Collective`

   A **concurrent**, **ordered** collection that manages items along with 
   their IDs, preserves insertion order via an internal :class:`Progression`, 
   and enforces optional type constraints. A :class:`Pile` is also 
   **async-compatible**, providing methods like ``asetitem``, ``apop``, 
   and ``aupdate`` for cooperative concurrency.

   Attributes
   ----------
   collections : dict[IDType, T]
       A dictionary mapping each item's unique ID to the actual item.
   item_type : set[type[T]] | None
       A set of allowed item types. If None, any :class:`Observable` is allowed.
   progression : Progression
       Tracks the **order** of items by their IDs.
   strict_type : bool
       If True, items must match exactly one of the `item_type` classes 
       (no subclassing allowed). If False, subclasses are also valid.

   Notes
   -----
   - Thread safety is provided via an internal lock, used in 
     :func:`synchronized`-decorated methods.
   - Asynchronous methods use an async lock, managed by 
     :func:`async_synchronized`.

   Initialization
   -------------
   .. method:: __init__(collections: ID.ItemSeq | None = None, item_type: set[type[T]] | None = None, order: ID.RefSeq | None = None, strict_type: bool = False, **kwargs)

      Creates a new ``Pile`` with optional initial items, item type constraints, 
      a custom order, and a strict-type toggle.

      Parameters
      ----------
      collections : ID.ItemSeq | None
          The initial set of items (could be a list, dict, or 
          :class:`~lionagi.protocols._concepts.Collective`).  
      item_type : set[type[T]] | None
          A set of permitted item types. If not provided, any :class:`Observable` 
          is allowed.  
      order : ID.RefSeq | None
          A predetermined ordering or references for the items. 
      strict_type : bool
          Whether to enforce **exact** type matching for each item 
          (subclasses not allowed if True).

   Core Methods (Synchronous)
   --------------------------
   The following synchronous methods are locked with :func:`synchronized`:

   .. method:: pop(key: ID.Ref | ID.RefSeq | int | slice, default: D = UNDEFINED) -> T | Pile | D

      Removes and returns item(s) indexed by ``key``. If not found and 
      ``default`` is provided, returns ``default`` instead of raising an error.

   .. method:: remove(item: T) -> None

      Removes a *specific item* if present. Raises a ``ValueError`` if not found.

   .. method:: include(item: ID.ItemSeq | ID.Item) -> None

      Adds item(s) if not already present.

   .. method:: exclude(item: ID.ItemSeq | ID.Item) -> None

      Excludes/removes item(s) if present.

   .. method:: clear() -> None

      Clears **all** items from the pile.

   .. method:: update(other: ID.ItemSeq | ID.Item) -> None

      Updates the pile with items from another source. Existing items are 
      replaced if they match IDs, or newly included if not present.

   .. method:: insert(index: int, item: T) -> None

      Inserts a single item at the given index. 

   .. method:: append(item: T) -> None

      Appends a single item to the end. (Alias for including one item.)

   .. method:: get(key: ID.Ref | ID.RefSeq | int | slice, default: D = UNDEFINED) -> T | Pile | D

      Retrieves item(s) from the pile, returning ``default`` if the key is not found 
      and a default is given.

   Additional Synchronous Accessors
   --------------------------------
   .. method:: keys() -> Sequence[str]

      Returns a list of item IDs (as strings) in the current order.

   .. method:: values() -> Sequence[T]

      Returns the list of items in order.

   .. method:: items() -> Sequence[tuple[IDType, T]]

      Returns (ID, item) pairs in order.

   .. method:: is_empty() -> bool

      Checks if the pile is empty.

   .. method:: size() -> int

      Returns the number of items in the pile.

   Overridden Python Dunder Methods
   --------------------------------
   .. method:: __len__() -> int

      Returns the number of items in the pile (same as :meth:`size`).

   .. method:: __iter__() -> Iterator[T]

      Iterates over items in the pile according to the internal order.

   .. method:: __contains__(item: ID.RefSeq | ID.Ref) -> bool

      Checks if an item or ID reference is in the pile.

   .. method:: __bool__() -> bool

      Returns True if the pile is not empty.

   .. method:: __str__() -> str
      :override:

      Simple string with the size, e.g., "Pile(3)".

   .. method:: __repr__() -> str
      :override:

      Detailed representation, e.g., "Pile()" if empty, "Pile(1 item)" 
      if one item, or "Pile(<n> items)" if multiple items.

   Async Methods
   -------------
   The following methods are decorated with :func:`async_synchronized`:

   .. method:: asetitem(key: ID.Ref | ID.RefSeq | int | slice, item: ID.ItemSeq | ID.Item) -> None

      Async equivalent of ``__setitem__``.

   .. method:: apop(key: ID.Ref | ID.RefSeq | int | slice, default: Any = UNDEFINED) -> Any

      Async version of :meth:`pop`.

   .. method:: aremove(item: ID.Ref | ID.RefSeq) -> None

      Async version of :meth:`remove`.

   .. method:: ainclude(item: ID.ItemSeq | ID.Item) -> None

      Async version of :meth:`include`.

   .. method:: aexclude(item: ID.Ref | ID.RefSeq) -> None

      Async version of :meth:`exclude`.

   .. method:: aclear() -> None

      Async version of :meth:`clear`.

   .. method:: aupdate(other: ID.ItemSeq | ID.Item) -> None

      Async version of :meth:`update`.

   .. method:: aget(key: Any, default=UNDEFINED) -> Any

      Async version of :meth:`get`.

   .. method:: __aiter__() -> AsyncIterator[T]

      Provides an async iterator over the items in the pile.

   File Export & Import
   --------------------
   Pile supports **adapters** for JSON, CSV, Excel, and Pandas DataFrame format.  
   Some key methods:

   .. method:: to_df(columns: list[str] | None = None, **kwargs) -> pd.DataFrame

      Converts the pile's data to a pandas DataFrame via the Pandas adapter.

   .. method:: to_csv_file(fp: str | Path, **kwargs) -> None

      Exports the items to a CSV file using the CSV adapter.

   .. method:: to_json_file(path_or_buf, use_pd: bool = False, mode="w", verbose=False, **kwargs) -> None

      Saves the pile to a JSON file. By default uses a basic JSON dump, 
      but if ``use_pd`` is True, uses pandas to export.

   .. classmethod:: adapt_from(obj: Any, obj_key: str, **kwargs)

      Creates a ``Pile`` from an external source (like a file path, 
      DataFrame, or JSON object) by invoking the matching adapter.

   .. method:: adapt_to(obj_key: str, **kwargs: Any) -> Any

      Converts this ``Pile`` to another format (e.g., a DataFrame or JSON) 
      via the registered adapters.

   Operators for Set-Like Behaviors
   --------------------------------
   Pile implements some set-inspired methods. For instance:

   .. method:: __or__, __ior__
      Union or in-place union with another pile.

   .. method:: __xor__, __ixor__
      Symmetric difference or in-place symmetric difference.

   .. method:: __and__, __iand__
      Intersection or in-place intersection.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.generic.pile import Pile
       from lionagi.protocols.generic.element import Element

       class MyItem(Element):
           pass

       p = Pile()
       item1, item2 = MyItem(), MyItem()
       p.include(item1)
       p.append(item2)
       print(p)  # e.g. "Pile(2)"

       # Export to CSV
       p.to_csv_file("mypile.csv")


pile
----
.. function:: pile(collections: Any = None, /, item_type: type[T] | set[type[T]] | None = None, progression: list[str] | None = None, strict_type: bool = False, df: pd.DataFrame | None = None, fp: str | Path | None = None, **kwargs) -> Pile
   :module: lionagi.protocols.generic.pile

   A **factory** function for creating a :class:`Pile` with flexible input. It 
   inspects parameters (e.g., a DataFrame or file path) to automatically pick 
   the correct adapter if needed. Otherwise, it just instantiates a normal 
   ``Pile`` with the given collections, type, and ordering.

   Parameters
   ----------
   collections : Any
       Initial items for the pile. Could be a single item, a list/tuple, 
       or a dictionary of items.
   item_type : type[T] | set[type[T]] | None
       Allowed element types (must inherit from :class:`Observable`). 
       If None, no restriction besides inheriting :class:`Observable`.
   progression : list[str] | None
       A preset order of item IDs.
   strict_type : bool
       If True, enforce exact type matches against ``item_type``.
   df : pd.DataFrame | None
       If provided, creates a pile from a pandas DataFrame using the 
       "pd_dataframe" adapter (highest priority).
   fp : str | Path | None
       A filepath for CSV/JSON/Excel from which to create a pile 
       (priority 2).

   Returns
   -------
   Pile
       A new pile instance.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.generic.pile import pile

       # Create from a CSV file
       p = pile(fp="data.csv")

       # Create from a DataFrame
       import pandas as pd
       df = pd.DataFrame({...})
       p2 = pile(df=df, item_type=MyItem)


Helper Functions
---------------
.. function:: to_list_type(value: Any) -> list[Any]
   :module: lionagi.protocols.generic.pile

   Converts the input into a **list** format for internal handling:

   - If None, returns [].
   - If already a list, tuple, set, or deque, returns a list copy.
   - If a string or :class:`IDType`, attempts to validate or wrap 
     as an ID.  
   - Otherwise returns [value].

   Used internally by the :class:`Pile` for consistent item parsing.

File Location
-------------
**Source File**: 
``lionagi/protocols/generic/pile.py``

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
