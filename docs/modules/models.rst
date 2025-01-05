=======================================
Model System
=======================================

This module provides foundational classes and utilities for **dynamically** 
creating and managing data models within LionAGI. These “operatives” form the 
building blocks of the system, offering features like:

- **Runtime field creation** (add, update, remove fields)
- **Nested validation** via Pydantic
- **Hashing/serialization** for easy storage and transport
- **Schema generation** (via :class:`FieldModel` and :class:`ModelParams`)

Below is an overview of the major components in this subsystem.



----------------------------
1. FieldModel (``field_model.py``)
----------------------------
.. module:: lionagi.operatives.model.field_model
   :synopsis: Structured definition of Pydantic fields.

.. class:: FieldModel
   :extends: SchemaModel

A configurable **field definition** that captures:

- **Name** (str)
- **Annotation** (type or Any)
- **Default** or **default_factory**  
- Optional **validator** (a function)
- Documentation info (title, description, examples)
- Additional Pydantic flags (e.g. ``exclude``, ``deprecated``, etc.)

**Usage**::

   from lionagi.operatives.model.field_model import FieldModel

   field = FieldModel(
       name="age",
       annotation=int,
       default=0,
       description="User age in years",
       validator=lambda cls, v: v if v >= 0 else 0
   )
   # Then use field.field_info or field.field_validator as needed


----------------------------
2. ModelParams (``model_params.py``)
----------------------------
.. module:: lionagi.operatives.model.model_params
   :synopsis: Dynamically create new Pydantic models.

.. class:: ModelParams
   :extends: SchemaModel

Collects **configuration** for generating a new Pydantic model class, such as:

- :attr:`parameter_fields`: a dictionary mapping field names to 
  :class:`FieldInfo`.
- :attr:`field_models`: a list of :class:`FieldModel` objects.
- :attr:`exclude_fields`: a list of fields to remove from the final model.
- :attr:`inherit_base`: Whether to extend a base model class (default: True).
- :attr:`config_dict`: Pydantic config overrides (e.g., ``frozen=True``).
- :attr:`doc`: Docstring for the generated model.

Finally, call :meth:`create_new_model()` to get a brand-new Pydantic class 
(with your specified fields, validators, docstring, etc.).

**Example**::

   from pydantic import BaseModel
   from lionagi.operatives.model.model_params import ModelParams
   from lionagi.operatives.model.field_model import FieldModel

   params = ModelParams(
       name="DynamicUser",
       base_type=BaseModel,
       field_models=[
           FieldModel(name="username", annotation=str, default="guest"),
           FieldModel(name="age", annotation=int, default=0),
       ],
       doc="Dynamically created user model."
   )
   DynamicUser = params.create_new_model()
   user = DynamicUser(username="Alice", age=30)
   print(user)   # => DynamicUser(username='Alice', age=30)


---------------------------
3. OperableModel (``operable_model.py``)
---------------------------
.. module:: lionagi.operatives.model.operable_model
   :synopsis: Extends Pydantic for dynamic field management.

.. class:: OperableModel
   :extends: HashableModel

This is a Pydantic model that allows **runtime** modifications to its schema,
including:

- :meth:`add_field(name, value=..., annotation=...)`: Add a new field.
- :meth:`update_field(...)`: Update an existing field or create if absent.
- :meth:`remove_field(name)`: Remove a field.

All **extra fields** are stored in :attr:`extra_fields` (mapping from 
name to :class:`pydantic.FieldInfo`) and :attr:`extra_field_models` 
(mapping from name to :class:`FieldModel`). The underlying dictionary 
structure remains valid with Pydantic’s type checks and serialization logic.

**Example**::

   from lionagi.operatives.model.operable_model import OperableModel

   class User(OperableModel):
       name: str = "default_name"

   user = User()
   user.add_field("age", value=25, annotation=int)
   print(user.age)  # => 25
   user.update_field("age", value=26)
   print(user.age)  # => 26
   user.remove_field("age")


--------------------------
4. Note (``note.py``)
--------------------------
.. module:: lionagi.operatives.model.note
   :synopsis: A flexible container for nested data.

.. class:: Note
   :extends: pydantic.BaseModel

A specialized object for **managing nested dictionary data**:

- :meth:`get(indices, default)`, :meth:`set(indices, value)`, :meth:`pop(indices)`, 
  etc. for deeply nested access or updates.
- :meth:`update(indices, value)` merges with an existing dict or appends to a list.
- :meth:`keys(flat=True|False)`: Optionally flatten nested structures.

It's a convenient alternative to constantly handling deeply nested dictionaries 
manually in your code.

**Example**::

   from lionagi.operatives.model.note import Note

   note = Note(user={"name": "John", "settings": {"theme": "dark"}})
   name = note.get(["user", "name"])  # "John"
   note.update(["user", "settings"], {"language": "en"})
   print(note.content)
   # => {"user": {"name": "John", "settings": {"theme": "dark", "language": "en"}}}


--------------------------
5. SchemaModel (``schema_model.py``)
--------------------------
.. module:: lionagi.operatives.model.schema_model
   :synopsis: Base model with restricted config and custom `keys()` method.

.. class:: SchemaModel
   :extends: HashableModel

A lightweight extension of :class:`HashableModel` that sets Pydantic config 
to **forbid** extra fields by default and use enum values. Provides a 
:method:`keys()` utility that returns the field names defined in the schema.


-------------------------
6. HashableModel (``hashable_model.py``)
-------------------------
.. module:: lionagi.operatives.model.hashable_model
   :synopsis: Adds hashing to Pydantic models.

.. class:: HashableModel
   :extends: pydantic.BaseModel

Enables your model to be **hashable**, so it can be used as keys in a 
dictionary or placed in a set. It does this by converting all fields to 
a dictionary (via :meth:`to_dict`) and then hashing the sorted key-value pairs.

**Note**: Some fields may need to be serialized or converted to strings if 
they are not inherently hashable.

**Example**::

   from lionagi.operatives.model.hashable_model import HashableModel

   class MyConfig(HashableModel):
       alpha: float
       beta: str

   c1 = MyConfig(alpha=1.0, beta="test")
   c2 = MyConfig(alpha=1.0, beta="test")
   s = {c1, c2}
   print(len(s))  # => 1 because c1 and c2 have the same hash


---------------------
Putting It All Together
---------------------
**Typical use case** for these model classes:

1. **Define** a base model with core fields (like a user or config).
2. **Add** or **update** fields at runtime if the structure is not fixed 
   (e.g., an “Operable” approach for flexible schemas).
3. **Dynamically** create entire new models with :class:`ModelParams` 
   (for advanced code generation scenarios).
4. Store nested data in :class:`Note` objects for iterative or 
   complicated updates.
5. Output or persist model objects as needed; they can be hashed, 
   used as dictionary keys, or automatically **serialized** with 
   LionAGI’s adapter system.

This design allows building truly “operable” data structures in a 
**dynamic** environment—where the model schema might evolve during runtime, 
and you need robust type checking, validation, and hashing to 
maintain data integrity.
