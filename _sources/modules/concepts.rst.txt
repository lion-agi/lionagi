.. _lionagi-core-abc:

====================================
Abstract Concepts
====================================
.. module:: lionagi.protocols._concepts
   :synopsis: Abstract base classes for LionAGI core concepts.

These abstract base classes (ABCs) describe fundamental “roles” or “capabilities”
that a LionAGI component can fulfill. They do **not** provide direct implementation
details, but establishing them ensures that different parts of the system 
communicate consistently and can be extended more reliably.


Observer
--------
.. class:: Observer
   :module: lionagi.protocols._concepts

   An **abstract base** (marker or interface) for all observer classes in LionAGI.
   Observers may be notified of events or changes in the system. Concrete classes
   that inherit ``Observer`` typically override or implement methods to react
   to these events (e.g., for logging or custom state updates).


Manager
-------
.. class:: Manager
   :module: lionagi.protocols._concepts

   **Inherits from**: :class:`Observer`

   A “manager” is a registry or controller that administers certain objects in
   the system. For instance, :class:`~lionagi.action.manager.ActionManager`
   manages callable tools, while a :class:`~lionagi.protocols.generic.log.LogManager`
   might manage log entries. By inheriting from ``Manager``, a class signifies
   that it orchestrates or keeps track of a set of resources within LionAGI.


Relational
----------
.. class:: Relational
   :module: lionagi.protocols._concepts

   **Inherits from**: None (abstract base)

   Used for **graph-connectable** objects. Classes implementing ``Relational``
   can be part of a graph data structure (e.g., nodes in a knowledge graph).
   Typically, such classes store references to edges or neighboring elements.


Sendable
--------
.. class:: Sendable
   :module: lionagi.protocols._concepts

   An abstract base for message-oriented capabilities. A “sendable” entity
   must track a **sender** identity and potentially a **recipient**, enabling
   the system to pass or route messages. Often used in queue-based or event-driven
   scenarios for multi-agent communication.


Observable
----------
.. class:: Observable
   :module: lionagi.protocols._concepts

   **Purpose**: Denotes an object that has an ``id`` field of a known type (usually
   a UUID). The object is thus “observable,” allowing references or logs to
   identify it unambiguously. Many core LionAGI classes implement ``Observable``
   so they can be stored or indexed by ID.


Communicatable
--------------
.. class:: Communicatable(Observable)
   :module: lionagi.protocols._concepts

   Combines an :attr:`id` (from :class:`Observable`) with **mailbox**-style
   communication. A “communicatable” class can have:

   - A mailbox or channel for inbound messages.
   - A :meth:`send()` method to emit messages to other recipients.

   This underlies multi-agent or multi-branch messaging in LionAGI.


Condition
---------
.. class:: Condition
   :module: lionagi.protocols._concepts

   An abstract base specifying a single **async** method:

   .. code-block:: python

      async def apply(self, *args, **kwargs) -> bool:
          ...

   Typically used for permission or constraint checks. For example,
   :class:`~lionagi.protocols.graph.edge.EdgeCondition` determines if an edge
   can be traversed. This method can do I/O or other async operations to decide
   True/False.


Collective
----------
.. class:: Collective(Generic[E])
   :module: lionagi.protocols._concepts

   A base for **collections** of items. Must define:

   - :meth:`include(item)`
   - :meth:`exclude(item)`

   Subclasses, like :class:`~lionagi.protocols.generic.pile.Pile`, store
   items with concurrency support or type constraints.


Ordering
--------
.. class:: Ordering(Generic[E])
   :module: lionagi.protocols._concepts

   Similar to :class:`Collective`, but emphasizes a **strict sequence** of items.
   Must define how items are inserted or removed while preserving an order. E.g.,
   :class:`~lionagi.protocols.generic.progression.Progression` that keeps an ordered
   list of IDs.


------------------------------
ID System and ``Element``
------------------------------
.. _lionagi-id-system:

.. module:: lionagi.protocols.generic.element
   :synopsis: Core ID-based classes and the Element base class.

LionAGI uses a **UUIDv4-based** scheme to ensure each object is uniquely 
identifiable. These classes unify that approach, providing hashing/equality
logic and a base class called :class:`Element` that includes:

- A unique ID field,
- A creation timestamp,
- A metadata dictionary for user-defined data.


IDType
------
.. class:: IDType
   :module: lionagi.protocols.generic.element

   A **lightweight** wrapper around a version-4 UUID. It enforces:

   - Validation of input strings to confirm valid v4 UUIDs.
   - Creation of random new UUIDs with :meth:`create()`.
   - Simple equality/hashing so that ID objects can be dict keys or set members.


ID
--
.. class:: ID(Generic[E])
   :module: lionagi.protocols.generic.element

   A utility class that helps **convert** various inputs (string, :class:`Element`, etc.)
   into a validated :class:`IDType`.  
   - :meth:`get_id(item) -> IDType`: Create or verify a valid ID.
   - :meth:`is_id(item) -> bool`: Quickly check if item is recognized as an ID.


Element
-------
.. class:: Element
   :module: lionagi.protocols.generic.element

   **Inherits from**: pydantic.BaseModel

   A **base class** for any LionAGI object needing:

   - A unique :attr:`id` (UUID v4).
   - A :attr:`created_at` timestamp (float, Unix epoch).
   - A :attr:`metadata` dictionary for custom fields.

   Also provides:

   - :meth:`to_dict()` for easy serialization,
   - Overridden ``__eq__`` and ``__hash__`` comparing objects by their :attr:`id`.

   **Example**::

      from lionagi.protocols.generic.element import Element

      class MyElement(Element):
          pass

      e = MyElement()
      print(e.id)        # => IDType
      print(e.metadata)  # => {}
      # Now e can be placed into a dictionary keyed by e.id


---------
Summary
---------
These **abstract concepts** and **ID-based data models** form the core of LionAGI:

- “**Roles**” like :class:`Observer`, :class:`Manager`, :class:`Relational`,
  etc., guide how classes are shaped and how they interact (managing tools, 
  sending messages, etc.).
- **Conditions** for controlling certain transitions or checks.
- The **ID** architecture ensures a universal reference scheme across 
  objects in logs, graphs, or concurrency managers.
- :class:`Element` standardizes an ID, timestamp, and metadata for every 
  signficant LionAGI component.
