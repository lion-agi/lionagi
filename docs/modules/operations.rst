=========================
``lionagi.operations``
=========================
The ``lionagi.operations`` package offers high-level “workflow” operations that build on
the messaging/``Instruct`` system. These operations tie together sequences of instructions
(i.e. multi-step tasks like planning, brainstorming, or selection).


----------------
Brainstorm Logic
----------------
.. module:: lionagi.operations.brainstorm
   :synopsis: Brainstorming multi-steps

**Key Exports**:

.. class:: BrainstormOperation

   A container model capturing:
   - ``initial``: The initial result from the brainstorming step.
   - ``brainstorm``: If you requested auto-run, the set of sub-instructions produced and run.
   - ``explore``: If you requested deeper exploration, the final expansions.

.. function:: brainstorm(instruct, num_instruct=2, session=None, branch=None, auto_run=True, auto_explore=False, ...)
   :async:

   High-level function to perform a brainstorming session in multiple steps:

   #. Generate an initial “brainstorm” output with up to `num_instruct` sub-ideas.
   #. (Optional) auto-run these sub-instructions.
   #. (Optional) “explore” the results from those sub-instructions, using a concurrency/queue strategy.

   **Returns** a :class:`BrainstormOperation` instance with all relevant data.

   **Parameters**:
   - **instruct** (Instruct | dict): The instruction or a dict with instruction data.
   - **session** (Session | None): If not provided, a new session is created.
   - **branch** (Branch | None): If not provided, a new branch is created in the session.
   - **auto_run** (bool): Whether to run sub-instructions automatically.
   - **auto_explore** (bool): If True, further expansions are done.
   - **explore_strategy**: One of “concurrent”, “sequential”, etc.
   - etc.

-----------------
Planning A Script
-----------------
.. module:: lionagi.operations.plan
   :synopsis: Multi-step plan generation

**Key Exports**:

.. class:: PlanOperation

   Stores:
   - ``initial``: The initial plan generation result
   - ``plan``: The steps (as a list of :class:`Instruct`)
   - ``execute``: The results if you auto-executed them.

.. function:: plan(instruct, num_steps=2, session=None, branch=None, auto_run=True, auto_execute=False, ...)
   :async:

   A multi-step plan approach:
   #. Prompt for a plan of up to `num_steps`.
   #. Optionally auto-run each step (expanding them).
   #. Optionally “execute” them via a concurrency strategy.

   **Returns** a :class:`PlanOperation` summarizing the entire plan.

---------------
Selection Logic
---------------
.. module:: lionagi.operations.select
   :synopsis: Selecting from sets of choices

**Key Exports**:

.. class:: SelectionModel

   A Pydantic model for storing final selection(s).

.. function:: select(instruct, choices, max_num_selections=1, session=None, branch=None, ...)
   :async:

   Given a set of choices (strings, an Enum, or a dict), prompts for up to `max_num_selections`
   and returns a :class:`SelectionModel`.

-------------------
Common Prompt Logic
-------------------
.. module:: lionagi.operations.prompt
   :synopsis: Shared prompt strings

   This module typically contains constants like ``PROMPT``, used in the
   various high-level operations.

------------
Utility Code
------------
.. module:: lionagi.operations.utils
   :synopsis: Helper utilities for session/branch

**Key Exports**:

.. function:: prepare_session(session=None, branch=None, branch_kwargs=None) -> tuple[Session, Branch]

   Creates or retrieves a :class:`Session` and a :class:`Branch`.  
   Ensures that the branch is inside the session’s pile.

.. function:: prepare_instruct(instruct, prompt) -> dict

   Merges a textual prompt into an existing instruct (dict or :class:`Instruct`).
