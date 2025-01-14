.. _lionagi_protocols_generic_element:

=======================================================
Element, IDType, and ID
=======================================================
.. module:: lionagi.protocols.generic.element
   :synopsis: Provides core ID handling and an Element base class for LionAGI.

Overview
--------
This module contains classes and functions that handle **UUID-based IDs**, 
simple identity checks, and a foundational :class:`Element` class built on 
Pydantic. With these abstractions, other parts of the system can reliably 
create and reference unique objects by ID, track metadata, and manage 
timestamps.


IDType
------
.. class:: IDType
   :module: lionagi.protocols.generic.element

   A **lightweight wrapper** around a UUID (preferably version 4). It ensures 
   valid UUIDv4 strings can be created or parsed, and supports hashing/equality 
   so instances can be used as dictionary keys or set members.

   Attributes
   ----------
   _id : UUID
       The wrapped UUID object.

   Notes
   -----
   - Use :meth:`create` to generate a random version-4 UUID.
   - Use :meth:`validate` to convert user inputs (strings, UUIDs, or 
     existing :class:`IDType` objects) into a proper ``IDType``.

   Methods
   -------
   .. method:: __init__(id: UUID) -> None

      Initializes the wrapper with a given UUID (ideally v4).

   .. classmethod:: validate(value: str | UUID | IDType) -> IDType

      Validates and converts a string, UUID, or existing IDType into a 
      proper ``IDType``. Raises :class:`lionagi._errors.IDError` 
      if the input is invalid.

   .. classmethod:: create() -> IDType

      Creates a new ``IDType`` with a randomly generated v4 UUID.

   .. method:: __str__() -> str

      Returns the string representation of the underlying UUID.

   .. method:: __repr__() -> str

      Developer-friendly representation for debugging, e.g. ``IDType(XXXX)``.

   .. method:: __eq__(other: Any) -> bool

      Checks equality based on the underlying UUID.

   .. method:: __hash__() -> int

      Returns a hash so ``IDType`` can serve as a dictionary key.


Element
-------
.. class:: Element
   :module: lionagi.protocols.generic.element

   **Inherits from**: :class:`pydantic.BaseModel`, :class:`lionagi.protocols._concepts.Observable`

   A **Pydantic-based** class that provides a **unique ID**, a **creation timestamp**, 
   and a flexible metadata dictionary. This forms a foundation for many other 
   LionAGI components that need to be both **observable** and **serializable**.

   Attributes
   ----------
   id : IDType
       A unique identifier (UUIDv4). Defaults to a newly generated one.
   created_at : float
       A float-based Unix timestamp. Defaults to current time.
   metadata : dict
       A dictionary for storing additional user-defined data.

   Methods
   -------
   .. classmethod:: class_name(full: bool = False) -> str

      Returns either the class name (e.g., ``Element``) or the fully qualified 
      path (e.g., ``lionagi.protocols.generic.element.Element``) depending 
      on the ``full`` flag.

   .. method:: to_dict() -> dict

      Converts this Element into a dictionary, appending the 
      ``"lion_class"`` field to metadata for class identification. 
      Fields that are :data:`lionagi.utils.UNDEFINED` are omitted.

   .. classmethod:: from_dict(data: dict) -> Element

      Creates an Element or Element subclass instance from a dictionary. 
      If the dictionary metadata includes a ``lion_class`` different from 
      this class, it attempts a dynamic lookup or import of that subclass.

   Notes
   -----
   - The Pydantic validators ensure that ``id`` is always a valid :class:`IDType` 
     and ``created_at`` is a float-based timestamp.
   - Instances of ``Element`` are hashable and can be used as dictionary keys 
     (hashing by their :attr:`id`).


validate_order
--------------
.. function:: validate_order(order: Any) -> list[IDType]
   :module: lionagi.protocols.generic.element

   Validates and flattens an **ordering** structure into a list of 
   :class:`IDType` objects. Accepts various input forms—like a single :class:`Element`, 
   a list of items, or a mapping (dictionary) of items—and ensures a consistent 
   flat list of IDs.

   Parameters
   ----------
   order : Any
       A potentially nested structure of items, each item possibly being an 
       :class:`Element`, a string, a :class:`UUID`, or an :class:`IDType`.

   Returns
   -------
   list[IDType]
       A flat list of validated :class:`IDType` objects.

   Raises
   ------
   ValueError
       If any item cannot be converted to an :class:`IDType` or if inconsistent 
       types are encountered.

   Examples
   --------
   Basic usage with a single :class:`Element`:
   
   .. code-block:: python

       element = SomeElementSubclass()
       order_list = validate_order(element)
       # order_list is now [element.id]

   Passing a nested list of elements or strings:

   .. code-block:: python

       items = [element1, "7acf8c04-3c6b-4edf-b221-e90c88f24fc0", [element2, element3]]
       order_list = validate_order(items)
       # returns a flat list of IDType objects


ID
--
.. class:: ID(Generic[E])
   :module: lionagi.protocols.generic.element

   A utility class for **extracting IDs** from various inputs and 
   **checking** if an object qualifies as an ID. Useful in code that must 
   handle Elements, raw strings (representing UUIDs), or :class:`IDType` 
   objects interchangeably.

   Type Parameters
   --------------
   E : :class:`Element`
       Constrains the generic type to elements that inherit from :class:`Element`.

   Aliases
   -------
   ID : TypeAlias
       Refers to :class:`IDType`.
   Item : TypeAlias
       Can be an instance of ``E`` or :class:`Element`.
   Ref : TypeAlias
       Can be an :class:`IDType`, an Element, or a UUID string.
   IDSeq : TypeAlias
       Sequence of :class:`IDType` or an :class:`Ordering[E]`.
   ItemSeq : TypeAlias
       Sequence of type ``E`` or a :class:`Collective[E]`.
   RefSeq : TypeAlias
       A union of :class:`ItemSeq`, a sequence of references, or :class:`Ordering[E]`.

   Methods
   -------
   .. staticmethod:: get_id(item: E) -> IDType

      Retrieves an :class:`IDType` from multiple item forms. If the item is 
      already an Element, returns its ``id``. If it's a string or a UUID, 
      validates it as a v4 UUID. Raises ``ValueError`` if conversion fails.

   .. staticmethod:: is_id(item: Any) -> bool

      Checks whether the given object can be validated as an :class:`IDType`. 
      Returns ``True`` if it's a valid ID, else ``False``.

   Example
   -------
   .. code-block:: python

       from uuid import uuid4
       from lionagi.protocols.generic.element import ID, Element, IDType

       class MyElement(Element):
           pass

       elem = MyElement()
       print(ID.get_id(elem))   # -> IDType(...)
       print(ID.is_id(uuid4())) # -> True


File Location
-------------
**Source File**: 
``lionagi/protocols/generic/element.py``

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
