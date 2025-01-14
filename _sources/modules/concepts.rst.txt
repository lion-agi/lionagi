.. _lionagi_protocols_concepts:

=======================================================
Abstract Concepts
=======================================================
.. module:: lionagi.protocols._concepts
   :synopsis: Defines fundamental abstract base classes that shape LionAGI's roles and capabilities.

Overview
--------
These classes outline the base “roles” in LionAGI—such as observation, management, 
and graph connectivity—without providing direct implementations. They ensure a 
consistent interface across different parts of the system. Subclasses must implement 
the required methods or attributes to fulfill each role.


Observer
--------
.. class:: Observer
   :module: lionagi.protocols._concepts

   Base abstract class for **observer** entities. An “observer” typically monitors or reacts 
   to changes in the system. Since it is an abstract marker, any class inheriting from 
   ``Observer`` may define custom methods for responding to events, logging updates, 
   or other side effects.

   Notes
   -----
   This class does not specify any methods; it simply designates the conceptual role of 
   an “observer” in LionAGI.


Manager
-------
.. class:: Manager
   :module: lionagi.protocols._concepts

   **Inherits from**: :class:`Observer`

   A “manager” is a specialized observer that administers or orchestrates certain objects 
   in the system. Managers typically handle creation, updates, or deletions of resources. 
   They may also provide concurrency-safe or stateful operations to coordinate these objects.

   Notes
   -----
   The exact management logic is determined by subclasses. For example, a `LogManager` 
   might store and manage log entries, while other managers might oversee different 
   resource types.


Relational
----------
.. class:: Relational
   :module: lionagi.protocols._concepts

   Represents a **graph-connectable** object. In LionAGI, classes implementing ``Relational`` 
   can appear as nodes in a graph-like structure. They may store relationships (edges) 
   to neighbors or track references to other ``Relational`` elements.

   Notes
   -----
   This abstract base class does not prescribe how to store or access neighbors, but 
   indicates that the implementing class can integrate into a graph data model.


Sendable
--------
.. class:: Sendable
   :module: lionagi.protocols._concepts

   An abstract class indicating that an entity can send messages. This requires 
   that the concrete subclass define sender/recipient information (e.g., in an event 
   or queue-based system). Typical usage includes multi-agent architectures where 
   messages must be routed between participants.

   Notes
   -----
   “Sendable” implies the presence of a **sender** and **recipient** attribute (or 
   equivalent). This class does not define actual methods for sending messages, as 
   it merely establishes the conceptual requirement.


Observable
----------
.. class:: Observable
   :module: lionagi.protocols._concepts

   Denotes that an entity must possess an **id** field, often a UUID or similar unique identifier. 
   Many core LionAGI classes inherit from ``Observable`` to ensure they can be referenced, 
   logged, and tracked by a universal ID. This simplifies indexing or lookups across the system.

   Notes
   -----
   - Subclasses must provide a concrete implementation or storage for ``id``.
   - Typically used with concurrency-safe collections or logging frameworks.


Communicatable
--------------
.. class:: Communicatable(Observable)
   :module: lionagi.protocols._concepts

   **Inherits from**: :class:`Observable`

   A more specialized form of **observable** object that also supports 
   mailbox-based messaging. This means the subclass must define:

   - A mailbox or channel to receive messages.
   - A :meth:`send` method for dispatching messages.

   Methods
   -------
   .. method:: send(*args, **kwargs)
      :abstractmethod:

      Abstract method to send a message. Subclasses should implement the necessary 
      logic to route or deliver the message (e.g., placing it on a queue or 
      invoking a handler).

   Notes
   -----
   By inheriting from :class:`Observable`, a communicatable entity also guarantees 
   it has a unique ID. This is crucial for addressing messages.


Condition
---------
.. class:: Condition
   :module: lionagi.protocols._concepts

   Defines an **async** interface for condition checks. Subclasses must implement 
   an ``apply`` method returning a boolean indicating whether a given condition 
   is satisfied.

   Methods
   -------
   .. method:: apply(*args, **kwargs) -> bool
      :async:
      :abstractmethod:

      Run an asynchronous check to determine if the condition holds. Returns 
      ``True`` if the condition is met, else ``False``.

   Example
   -------
   A scheduling system might implement a condition that checks whether 
   a resource is available. This check could involve async I/O (e.g., an 
   external call), making the ``apply`` method asynchronous.


Collective
----------
.. class:: Collective(Generic[E])
   :module: lionagi.protocols._concepts

   Abstract base for **collections** of elements. A class implementing ``Collective`` 
   must provide at least two methods:

   - :meth:`include(item)`
   - :meth:`exclude(item)`

   These methods add or remove elements from the collection, respectively. The details 
   (e.g., concurrency, strict typing, ordering) are left to the subclass. 

   Methods
   -------
   .. method:: include(item, /)
      :abstractmethod:

      Insert the given item into the collection.

   .. method:: exclude(item, /)
      :abstractmethod:

      Remove the given item from the collection, if present.

   Notes
   -----
   Implementations such as :class:`~lionagi.protocols.generic.pile.Pile` provide 
   concurrency-safe storage and type enforcement on top of this base.


Ordering
--------
.. class:: Ordering(Generic[E])
   :module: lionagi.protocols._concepts

   Similar to :class:`Collective`, but emphasizes a **strict sequence** of elements. 
   This means order matters, and subclasses must define how items are inserted or 
   removed while preserving that sequence.

   Methods
   -------
   .. method:: include(item, /)
      :abstractmethod:

      Insert the given item while respecting an ordering structure. The exact 
      strategy (e.g., append, sorted insert, or custom rule) is determined by 
      the subclass.

   .. method:: exclude(item, /)
      :abstractmethod:

      Remove the given item, ensuring the overall sequence remains valid.

   Notes
   -----
   A prime example is :class:`~lionagi.protocols.generic.progression.Progression`, 
   which keeps a strictly ordered list of IDs or elements.

----

File Location
-------------
**Source File**: 
``lionagi/protocols/_concepts.py``

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``  
``SPDX-License-Identifier: Apache-2.0``
