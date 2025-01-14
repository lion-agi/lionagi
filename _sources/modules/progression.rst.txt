.. _lionagi_protocols_generic_progression:

=========================================================
Progression
=========================================================
.. module:: lionagi.protocols.generic.progression
   :synopsis: Implements a strictly ordered collection of IDs with optional naming.

Overview
--------
The :class:`Progression` class combines a list-like structure of IDs 
(:class:`IDType`) with the properties of an :class:`~lionagi.protocols._concepts.Ordering`.
It allows insertion, removal, and slicing while preserving a **strict sequence**
of items. The optional :attr:`name` field enables easy identification or labeling
of the progression. Also included is a convenience function, :func:`prog`, 
for quick creation of a new :class:`Progression`.


Progression
-----------
.. class:: Progression(Element, Ordering[E], Generic[E])
   :module: lionagi.protocols.generic.progression

   **Inherits from**:
   :class:`~lionagi.protocols.generic.element.Element`  
   :class:`~lionagi.protocols._concepts.Ordering`

   Tracks an ordered sequence of item IDs, plus an optional name. This class
   offers list-like methods such as indexing, slicing, insertion, and removal
   while ensuring that the items are all valid :class:`IDType` objects.

   Attributes
   ----------
   order : list[ID[E].ID]
       The stored list of IDs, each representing an element in the progression.
   name : str | None
       An optional string giving this progression a human-readable name.

   Validators & Serializers
   ------------------------
.. method:: _validate_ordering(value: Any) -> list[IDType]
   :classmethod:

   Private class method that ensures the given value is a valid list of IDs, flattening nested structures 
   via :func:`~lionagi.protocols.generic.element.validate_order`. Raises 
   :exc:`ValueError` if items are invalid.

.. method:: _serialize_order(value: list[IDType]) -> list[str]

   Private instance method that serializes each :class:`IDType` in the list into its UUID string 
   representation.

   Basic Methods
   -------------
   .. method:: __len__() -> int

      Returns the number of IDs in the progression.

   .. method:: __bool__() -> bool

      Returns ``True`` if the progression has at least one ID, otherwise ``False``.

   .. method:: __contains__(item: Any) -> bool

      Checks if *all* IDs in the given ``item`` (Element, IDType, UUID, 
      or a collection thereof) exist in this progression.

   .. method:: __getitem__(key: int | slice) -> IDType | list[IDType]

      Fetches either a single ID (if ``key`` is an int) or a new sub-Progression 
      (if ``key`` is a slice).

      Raises
      ------
      :exc:`lionagi._errors.ItemNotFoundError`
          If the requested index or slice is out of range.
      :exc:`TypeError`
          If ``key`` is neither an int nor a slice.

   .. method:: __setitem__(key: int | slice, value: Any) -> None

      Replaces items at the specified position(s) with new IDs validated 
      via :func:`~lionagi.protocols.generic.element.validate_order`.

   .. method:: __delitem__(key: int | slice) -> None

      Removes items at the specified position(s).

   Iteration & Utility
   -------------------
   .. method:: __iter__() -> Iterator[IDType]

      Iterates over the IDs in order.

   .. method:: __list__() -> list[IDType]

      Returns a shallow copy of the entire ``order`` list.

   .. method:: clear() -> None

      Clears all IDs from the progression.

   Collective-Like Methods
   ------------------------
   The following methods satisfy the :class:`~lionagi.protocols._concepts.Ordering`
   interface:

   .. method:: include(item: Any) -> bool

      Adds new IDs (if not already present). Returns ``True`` if at least one
      ID was appended, else ``False``.

   .. method:: exclude(item: Any) -> bool

      Removes occurrences of specified IDs. Returns ``True`` if one or more 
      items were removed, else ``False``.

   Additional List-Like Methods
   ----------------------------
   .. method:: append(item: Any) -> None

      Appends one or more validated IDs to the end of the progression.

   .. method:: pop(index: int = -1) -> IDType

      Removes and returns a single ID by index (defaulting to the last item).
      Raises :exc:`lionagi._errors.ItemNotFoundError` if the index is invalid.

   .. method:: popleft() -> IDType

      Removes and returns the first ID.
      Raises :exc:`lionagi._errors.ItemNotFoundError` if the progression is empty.

   .. method:: remove(item: Any) -> None

      Removes the *first* occurrence of each specified ID. Raises 
      :exc:`lionagi._errors.ItemNotFoundError` if any ID is not found.

   .. method:: count(item: Any) -> int

      Counts occurrences of a given ID in the progression.

   .. method:: index(item: Any, start: int = 0, end: int | None = None) -> int

      Finds the position of the first occurrence of an ID. Raises :exc:`ValueError` 
      if the ID is not found within the given range.

   .. method:: extend(other: Progression)

      Appends all IDs from another :class:`Progression` to this one. Raises
      :exc:`ValueError` if ``other`` is not a :class:`Progression`.

   .. method:: insert(index: int, item: ID.RefSeq) -> None

      Inserts one or more IDs at a specific index.

   Advanced Operators
   ------------------
   .. method:: __add__(other: Any) -> Progression[E]

      Returns a new :class:`Progression` with IDs from both this instance
      and ``other`` (validated).

   .. method:: __radd__(other: Any) -> Progression[E]

      Allows concatenation when this progression is on the right-hand side.

   .. method:: __iadd__(other: Any) -> Self

      In-place addition of IDs. Uses :meth:`append` under the hood.

   .. method:: __sub__(other: Any) -> Progression[E]

      Returns a new :class:`Progression` excluding any IDs in ``other``.

   .. method:: __isub__(other: Any) -> Self

      In-place removal of IDs found in ``other``. Uses :meth:`remove` 
      internally.

   .. method:: __reverse__() -> Progression[E]

      Returns a new reversed copy of the progression.

   .. method:: __eq__(other: object) -> bool

      Checks whether two progressions have the same :attr:`order` and 
      :attr:`name`.

   .. method:: __gt__(other: Progression[E]) -> bool

      Compares whether this progression's :attr:`order` is “greater.”

   .. method:: __lt__(other: Progression[E]) -> bool

      Compares whether this progression's :attr:`order` is “less.”

   .. method:: __ge__(other: Progression[E]) -> bool

      Greater-or-equal comparison by order.

   .. method:: __le__(other: Progression[E]) -> bool

      Less-or-equal comparison by order.

   .. method:: __repr__() -> str

      Developer-friendly string showing the :attr:`name` and :attr:`order`.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.generic.progression import Progression, prog
       from lionagi.protocols.generic.element import Element

       class MyElem(Element):
           pass

       elem1, elem2 = MyElem(), MyElem()

       # Create a new progression
       p = Progression(order=[elem1.id], name="My Progression")
       p.append(elem2)

       # Alternatively, use the `prog` function
       p2 = prog([elem1, elem2], name="Quickly Built")
       assert p2.name == "Quickly Built"


prog
----
.. function:: prog(order: Any, name: str = None) -> Progression
   :module: lionagi.protocols.generic.progression

   A **convenience** function to instantiate a new :class:`Progression` without 
   manually creating the object.

   Parameters
   ----------
   order : Any
       Any structure that can be validated by 
       :func:`~lionagi.protocols.generic.element.validate_order`, e.g., 
       a list of :class:`Element`, :class:`IDType`, or string-based UUIDs.
   name : str, optional
       A label for the newly created progression.

   Returns
   -------
   Progression
       The resulting progression containing the validated IDs.

File Location
-------------
**Source File**: 
``lionagi/protocols/generic/progression.py``

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
