============================================
Pile & Progression
============================================

``Pile`` and ``Progression`` are two powerful data structures that LionAGI
uses to store and manage elements in an **ordered** (or **partially ordered**)
fashion. Both classes leverage LionAGI's built-in :class:`Element` and
:class:`IDType` for consistent, UUID-based identification of items.


----------------------------
``Progression`` (progression.py)
----------------------------
.. module:: lionagi.protocols.generic.progression
   :synopsis: A strictly ordered sequence of UUIDs.

A :class:`Progression` represents a **simple, strictly ordered sequence** of
item IDs. It inherits from :class:`~lionagi.protocols.generic.element.Element`
(which provides it with a UUID-based identity and metadata) and from
:class:`~lionagi.protocols._concepts.Ordering`.

**Key Points**:

- Stores **only IDs** (of type :class:`IDType`) in a list, accessible via
  :attr:`order`.
- Offers **list-like** operations (``append``, ``insert``, slicing, etc.).
- Offers **set-like** operations for IDs (``+``, ``-``, intersection,
  difference, etc.).
- Can be labeled with a :attr:`name` attribute for easy reference.

.. class:: Progression(Generic[E])
   :module: lionagi.protocols.generic.progression

   Tracks a **strict ordering** of item IDs, typically referencing
   :class:`Element` objects stored elsewhere (for example, in a
   :class:`Pile`).

   **Attributes**:

   .. attribute:: order
      :type: list[IDType]
      A plain Python list of UUIDs (version-4) representing the progression's
      sequence. Each UUID references a separate :class:`Element` stored or
      managed elsewhere.

   .. attribute:: name
      :type: str | None
      An optional human-readable name/label for this progression. For
      example, you might call it “workflow_steps” or “node_sequence.”

   **Methods**:

   - **Append / Insert / Remove**:
     
     .. method:: append(item: Any) -> None

        Add a single ID (or item convertible to an ID) to the **end** of
        the progression.

     .. method:: include(item: Any) -> bool

        Add one or more IDs if not already present. Returns ``True``
        if at least one new item was added, or ``False`` otherwise.

     .. method:: exclude(item: Any) -> bool

        Remove one or more IDs if present. Returns ``True`` if at least
        one item was removed, or ``False`` otherwise.

     .. method:: insert(index: int, item: Any) -> None

        Insert one or more IDs at the given list position.

     .. method:: remove(item: Any) -> None

        Remove the **first** occurrence of each specified ID (raises
        :exc:`ItemNotFoundError` if not found).

   - **Slicing / Indexing**:
     
     Progression supports Pythonic slicing. For example:
     
     .. code-block:: python

        subprog = my_progression[0:3]  # returns a new Progression with the first 3 IDs

   - **Set-like operators**:
     
     .. code-block:: python

        new_prog = prog1 + prog2   # union (concatenation) of IDs
        diff_prog = prog1 - prog2  # remove IDs in prog2 from prog1

     These operations produce **new** Progression objects without mutating
     the originals.

   **Example**::

      from lionagi.protocols.generic.progression import Progression

      prog = Progression(name="MySequence")

      # Add IDs (these can be raw strings if they are valid UUIDs)
      prog.append("8299a0ea-96d2-4514-afaa-409ece7e63d9")
      prog.include([
          "35092634-3694-46c1-8f40-8ef85b349948",
          "4dbccfcc-9713-40dd-b36c-e9e29e1cbb8f"
      ])
      print(prog.order)
      # -> ['8299a0ea-96d2-4514-afaa-409ece7e63d9',
      #     '35092634-3694-46c1-8f40-8ef85b349948',
      #     '4dbccfcc-9713-40dd-b36c-e9e29e1cbb8f']

      # Remove an ID
      prog.remove("35092634-3694-46c1-8f40-8ef85b349948")

      # Slicing yields either a single ID or a new Progression
      first_id = prog[0]     # the first ID in the list
      subprog = prog[:1]     # a new Progression with just the first item

      print(subprog.order)
      # -> ['8299a0ea-96d2-4514-afaa-409ece7e63d9']


--------------------------
``Pile`` (pile.py)
--------------------------
.. module:: lionagi.protocols.generic.pile
   :synopsis: A thread-safe, async-compatible container for LionAGI elements.

A :class:`Pile` manages **actual objects** (subclasses of
:class:`~lionagi.protocols.generic.element.Element`), storing them in
a **dictionary** keyed by their UUID, while also tracking the **order** of
insertion via an internal :class:`Progression`.

**Key Points**:

- Each stored item **must** implement :class:`~lionagi.protocols._concepts.Observable`
  (i.e., have an :attr:`id` field).
- A Pile can optionally enforce **type constraints** via :attr:`item_type`.
- Internally uses a standard dict mapping ``{IDType -> item}`` plus a
  :class:`~lionagi.protocols.generic.progression.Progression` to remember the
  insertion order.
- Provides built-in **thread safety** (via a standard Python lock) and
  **async safety** (via an asyncio lock) for concurrent usage.

.. class:: Pile(Element, Collective[E], Generic[E])
   :module: lionagi.protocols.generic.pile

   Wraps a dictionary of ``{IDType: item}``, plus a progression to maintain
   insertion order. Offers many **synchronous** and **asynchronous** methods
   (e.g., ``pop()`` vs. ``apop()``, ``include()`` vs. ``ainclude()``, etc.)
   for safe usage in multi-threaded or async contexts.

   **Attributes**:

   .. attribute:: collections
      :type: dict[IDType, E]
      The underlying dictionary storing items by their ID.

   .. attribute:: item_type
      :type: set[type[E]] | None
      A set of allowable classes for the items in this Pile. If not ``None``,
      items must be instances or subclasses of these classes. If
      :attr:`strict_type` is ``True``, the item's **exact** class must match
      an entry in this set.

   .. attribute:: progression
      :type: Progression
      Maintains the order of the keys in :attr:`collections`.

   .. attribute:: strict_type
      :type: bool
      If ``True``, enforces that items exactly match a class in
      :attr:`item_type`. If ``False``, items may be subclasses of the specified
      type(s).

   **Thread / Async Locks**:

   The :class:`Pile` uses an internal lock (:attr:`lock`) for synchronous
   operations and an :attr:`async_lock` for asynchronous operations,
   ensuring that concurrent modifications do not corrupt internal state.

   **Core Methods**:

   - **Include / Exclude**:
     
     .. method:: include(item)
        Insert one or more items by generating their ID (if necessary) and storing
        them in the dictionary. If an item's ID already exists, it is skipped. The
        insertion order is appended to :attr:`progression`.

     .. method:: exclude(item)
        Remove one or more items (by ID) if found. No error if absent.

   - **Pop / Get**:
     
     .. method:: pop(key, default=UNDEFINED)
        Remove and return item(s) referenced by ``key`` (which can be an ID,
        a slice, or an integer index). If not found and no default is
        provided, raises :exc:`ItemNotFoundError`.

     .. method:: get(key, default=UNDEFINED)
        Retrieve item(s) referenced by ``key`` without removing them.
        If missing, return ``default`` or raise an error.

   - **Set / List operations**:
     
     .. code-block:: python

        # Union
        pile_c = pile_a | pile_b
        # Intersection
        pile_d = pile_a & pile_b
        # Symmetric difference
        pile_e = pile_a ^ pile_b

     When both operands are :class:`Pile` objects, these operations combine
     or filter the items accordingly.

   - **Dumping/Loading**:
     
     .. method:: to_csv_file(fp, **kwargs)
        Write items (serialized by :meth:`Element.to_dict`) to CSV.

     .. method:: to_json_file(fp, **kwargs)
        Write items to JSON, storing a dict with a ``"collections"`` key.

     A Pile can be reloaded from JSON or CSV by calling the :func:`pile` factory
     function with the ``fp`` parameter.

   **Async Methods**:

   Each major method (e.g., ``pop()``, ``include()``, etc.) has an async 
   equivalent (e.g., ``apop()``, ``ainclude()``), which acquires the 
   :attr:`async_lock`.

   **Example**::

      from lionagi.protocols.generic.pile import Pile
      from lionagi.protocols.generic.element import Element

      class MyItem(Element):
          # Extra fields, if needed
          pass

      # Create items
      item1 = MyItem(metadata={"tag": "alpha"})
      item2 = MyItem(metadata={"tag": "beta"})

      # Create a Pile enforcing type = MyItem
      p = Pile(item_type={MyItem}, strict_type=True)

      # Insert items
      p.include(item1)
      p.include(item2)

      # Access by index or ID
      first = p[0]         # item1
      second = p[item2.id] # item2

      # Slicing
      slice_ = p[:2]

      # Save to JSON
      p.to_json_file("my_pile.json")

      # Load from file
      from lionagi.protocols.generic.pile import pile
      p2 = pile(fp="my_pile.json")
      print(len(p2))  # Should match len(p)

      # Combining Piles
      # union
      p3 = p | p2
      print(len(p3))


--------------------
Comparison Overview
--------------------
+--------------------+------------------------------------------+--------------------------------------------+
| **Feature**        | **Progression**                          | **Pile**                                   |
+====================+==========================================+============================================+
| Inherits           | :class:`Element` + :class:`Ordering`     | :class:`Element` + :class:`Collective`     |
+--------------------+------------------------------------------+--------------------------------------------+
| Stores             | **List** of IDs (type :class:`IDType`).  | **Dict** of ``{IDType -> item}``, plus a   |
|                    | Each ID references a separate            | :class:`Progression` for consistent order. |
|                    | :class:`Element`.                        |                                            |
+--------------------+------------------------------------------+--------------------------------------------+
| Thread safety      | **No** built-in lock (intended for       | **Yes**: uses locks for both sync and      |
|                    | simpler single-thread or read-only).     | async usage.                               |
+--------------------+------------------------------------------+--------------------------------------------+
| Type enforcement   | **None** by default; it only stores ID   | **Optional**: can specify :attr:`item_type`|
|                    | strings referencing objects.             | and :attr:`strict_type` for stricter       |
|                    |                                          | class-based constraints.                   |
+--------------------+------------------------------------------+--------------------------------------------+
| Basic usage        | Maintaining a simple **ordered** list    | Maintaining a keyed dictionary with        |
| scenario           | of IDs (e.g. steps in a workflow).       | concurrency-safe reads/writes.            |
+--------------------+------------------------------------------+--------------------------------------------+
| File serialization | **None** built in. Typically you store   | CSV/JSON with :meth:`dump` or :meth:`to_   |
|                    | only references.                         | csv_file`/:meth:`to_json_file`.           |
+--------------------+------------------------------------------+--------------------------------------------+
| Example usage      | Quick ordering structure for BFS, DFS,   | Full container for storing actual items,   |
|                    | or chain-of-thought logs.                | often used in concurrency or large-scale  |
|                    |                                          | data management.                          |
+--------------------+------------------------------------------+--------------------------------------------+


----------
Summary
----------
- **Progression** is a minimal, strictly ordered list of IDs, suitable 
  for **lightweight** tracking of sequences (like workflows or chain-of-thought).

- **Pile** is a more robust, **thread-/async-safe** container, mapping IDs 
  to actual objects. It retains insertion order through an internal 
  :class:`Progression`, supports type enforcement, and offers CSV/JSON 
  serialization.

Together, **Progression** and **Pile** form a cohesive system for referencing
and managing LionAGI objects in an **orderly** and **concurrency-safe** manner,
whether you only need ID-based sequences (Progression) or a complex keyed
structure (Pile).
