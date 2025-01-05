================================
Instruct
================================

The **Instruct System** provides a flexible way to define and manage **instruction parameters** 
(e.g., a prompt, context, guidance, reason, or required actions) when building 
sophisticated workflows or LLM-driven tasks. It leverages Pydantic models 
(:class:`HashableModel`) for type safety and easy serialization, plus some 
specialized “field” definitions to ensure consistent validation and usage 
across LionAGI.  

Common usage patterns include:

- Embedding an :class:`Instruct` model within a larger data structure or 
  node (e.g., :class:`InstructNode`) that can be passed around to 
  orchestrate tasks.
- Managing collections of instructions (:class:`InstructCollection`) 
  for multi-step or multi-instruction pipelines.



----------------------
1. Core Instruct Fields
----------------------
.. module:: lionagi.operatives.instruct.base
   :synopsis: Defines the standard fields for instructions.

These “field models” are specialized definitions for typical 
“instruct” data points:

- **Instruction**: A primary instruction or objective (JSON-serializable).
- **Guidance**: Additional strategic/tactical hints.
- **Context**: Current environment or background info for the instruction.
- **Reason**: Whether or not (or how) reasoning is included.
- **Actions**: Whether actions are strictly required, optional, or not at all.

**List of Fields**:

.. py:data:: INSTRUCTION_FIELD
   :annotation: FieldModel
   The main task or objective.  
   Enforces that it’s a JSON-like object or None.

.. py:data:: GUIDANCE_FIELD
   :annotation: FieldModel
   Extra guidance about how the instruction should be handled 
   (methodology, constraints, etc.).

.. py:data:: CONTEXT_FIELD
   :annotation: FieldModel
   Information about the current environment or state relevant to 
   fulfilling the instruction.

.. py:data:: REASON_FIELD
   :annotation: FieldModel
   Boolean or specialized object controlling whether to produce 
   an explanatory “reasoning” or not.

.. py:data:: ACTIONS_FIELD
   :annotation: FieldModel
   Boolean controlling if tool usage or action invocations are 
   strictly required.


-------------------------
2. The ``Instruct`` Model
-------------------------
.. module:: lionagi.operatives.instruct.instruct
   :synopsis: Main class combining instruct fields.

.. class:: Instruct
   :extends: HashableModel

Consolidates the **instruction** pattern with standard fields:

- :attr:`instruction`: The user’s main objective 
  (type: ``JsonValue | None``).
- :attr:`guidance`: Extra pointers or constraints 
  (type: ``JsonValue | None``).
- :attr:`context`: Additional environment or prior state 
  (type: ``JsonValue | None``).
- :attr:`reason`: Boolean for whether reasoning is included 
  (or a separate struct).
- :attr:`actions`: Boolean controlling if actions are needed.

Example usage::

   from lionagi.operatives.instruct.instruct import Instruct

   instr = Instruct(
       instruction={"task": "Translate the text to French"},
       guidance={"style": "formal"},
       context={"source_language": "English", "topic": "greetings"},
       reason=True,
       actions=False,
   )
   print(instr.instruction)
   # => {"task": "Translate the text to French"}


InstructResponse
~~~~~~~~~~~~~~~~
.. class:: InstructResponse
   :extends: HashableModel

A simple container pairing an :attr:`instruct` (the 
:class:`Instruct` object) with a :attr:`response` (the 
final outcome from an LLM or other system).  Typically used 
to store results after an instruction is processed.


----------------------------
3. Instruct Collection
----------------------------
.. module:: lionagi.operatives.instruct.collection
   :synopsis: Manage multiple instructions in one model.

.. class:: InstructCollection
   :extends: pydantic.BaseModel

Holds multiple :class:`Instruct` objects (by default, 
fields named ``instruct_0``, ``instruct_1``, etc.). This 
lets you define a dynamic model that can contain an arbitrary 
number of instructions.

**Key Methods**:

- :meth:`instruct_models` -> list[Instruct]:  
  Gathers all ``instruct_*`` fields into a list.
- :meth:`create_model_params(num_instructs=3, **kwargs) -> ModelParams`:  
  Dynamically build a :class:`ModelParams` definition for 
  an InstructCollection with a specified count of instruct fields.
- :meth:`to_instruct_nodes() -> list[InstructNode]`:  
  Convert each instruct into an :class:`InstructNode`.

Usage::

   from lionagi.operatives.instruct.collection import InstructCollection

   class MyCollection(InstructCollection):
       pass

   # Create a model config for 2 instructions
   mp = MyCollection.create_model_params(num_instructs=2)
   # Then generate a new pydantic model from it, or instantiate.


----------------------
4. InstructNode
----------------------
.. module:: lionagi.operatives.instruct.node
   :synopsis: Node-based approach to storing an Instruct instance.

.. class:: InstructNode
   :extends: Node

A specialized :class:`Node` that includes an :attr:`instruct` 
field of type :class:`Instruct`. This is useful when building 
**graph** structures in LionAGI and embedding instructions 
directly in the graph’s nodes. For instance, each node in a 
workflow graph might carry specific instructions for LLM steps 
or sub-tasks.

Usage::

   from lionagi.operatives.instruct.node import InstructNode
   from lionagi.operatives.instruct.instruct import Instruct

   node = InstructNode(
       instruct=Instruct(
           instruction={"task": "Summarize text"},
           guidance={"style": "brief"},
       )
   )
   print(node.instruct.instruction)  # => {"task": "Summarize text"}


------------------------------
5. Example: Combining Instruct
------------------------------
A common pattern might be to define a custom model that includes 
an :class:`Instruct` (or a list of them). For example, if you 
have a multi-step LLM pipeline:

.. code-block:: python

   from pydantic import BaseModel
   from lionagi.operatives.instruct.instruct import Instruct

   class MyPipelineStage(BaseModel):
       name: str
       instruct: Instruct

   stage = MyPipelineStage(
       name="Stage1",
       instruct=Instruct(
           instruction={"task": "Outline the main ideas"},
           reason=True,
       )
   )

   # The pipeline can handle 'stage.instruct' for LLM calls or tasks


---------------------
Summary
---------------------
The **LionAGI Instruct System** provides:

- **Instruct**: A minimal, typed container for the main 
  instruction, guidance, context, and toggles like reason 
  or actions.
- **InstructCollection**: A dynamic approach to storing 
  multiple instructions.
- **InstructNode**: When you need to embed an instruction 
  inside a graph node.

By standardizing instruction-related fields (like 
``instruction``, ``guidance``, ``context``), this system 
promotes consistent usage across different modules, 
**simplifying** the integration of instructions in 
LLM-based tasks or advanced multi-step flows.
