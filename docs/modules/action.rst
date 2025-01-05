.. _lionagi-action:

===========================
Action
===========================

This module provides a **flexible event-driven framework** for creating and managing
**callable “tools”** in LionAGI, validating their inputs/outputs, and invoking them
asynchronously with optional pre/post-processing steps. It integrates with the LionAGI
**event system** (see :class:`~lionagi.protocols.types.Event`), allowing each function call
to be tracked as an event—complete with execution duration, status, and error handling.

The primary components are:

- **Tool**: A wrapper for a Python callable function with validation.
- **ActionManager**: A registry that orchestrates tools.
- **FunctionCalling**: An :class:`~lionagi.protocols.types.Event` that tracks
  asynchronous function execution.
- **ActionRequestModel** / **ActionResponseModel**: Pydantic models for structuring
  inputs/outputs.

These classes can be combined with LionAGI's concurrency architecture—such as
:class:`~lionagi.protocols.generic.processor.Processor` and
:class:`~lionagi.protocols.generic.processor.Executor`—to manage multiple function calls
as events in a queue or stored in a :class:`~lionagi.protocols.generic.pile.Pile`
(ordered by a :class:`~lionagi.protocols.generic.progression.Progression`).


---------------------------
Module Organization & Files
---------------------------

The ``lionagi.action`` package comprises:

- **function_calling.py**:

  Contains :class:`FunctionCalling`, which is an event class for executing a
  single tool call asynchronously, handling optional pre/post processing,
  and storing timing/status in its :attr:`execution`.

- **manager.py**:

  Implements :class:`ActionManager`, a central registry to:

  - Register tools (functions).
  - Match incoming requests (function name + arguments) to a registered tool.
  - Create and run :class:`FunctionCalling` events, returning outcomes or errors.

- **request_response_model.py**:

  Defines the data schemas for requests/responses:

  - :class:`ActionRequestModel` — capturing the function name and arguments.
  - :class:`ActionResponseModel` — capturing output after the call.

- **tool.py**:

  Provides the :class:`Tool` class, wrapping a Python function with optional
  **preprocessor** / **postprocessor** steps, plus an auto-generated argument schema.

.. module:: lionagi.action


Tool
~~~~
.. class:: Tool

   A ``Tool`` wraps a Python callable (function) with metadata and (optionally)
   preprocessing/postprocessing. It can **strictly validate** the function's parameters,
   preventing extraneous or missing arguments.

   **Key Attributes**:

   .. py:attribute:: func_callable
      :type: Callable[..., Any]

      The underlying Python function. This may be sync or async.

   .. py:attribute:: tool_schema
      :type: dict[str, Any] | None

      An auto-generated JSON schema for the function's parameters (unless provided explicitly).

   .. py:attribute:: preprocessor
      :type: Callable[[dict[str, Any]], dict[str, Any]] | None

      Optional function that modifies/validates the incoming arguments.

   .. py:attribute:: postprocessor
      :type: Callable[[Any], Any] | None

      Optional function that modifies/validates the function's output.

   .. py:attribute:: strict_func_call
      :type: bool

      If ``True``, only the function's exact parameters are allowed during invocation.

   **Properties**:

   .. py:attribute:: function
      :type: str

      The function's name, inferred from the callable unless overridden.

   .. py:attribute:: required_fields
      :type: set[str]

      The parameter names that have no default in the function signature.

   .. py:attribute:: minimum_acceptable_fields
      :type: set[str]

      A less strict subset of required fields, determined by analyzing
      arguments vs. defaults.

   **Example**::

      from lionagi.action.tool import Tool

      def add(x: int, y: int) -> int:
          return x + y

      # Wrap 'add' with strict validation
      add_tool = Tool(
          func_callable=add,
          strict_func_call=True
      )


FunctionCalling
~~~~~~~~~~~~~~~
.. class:: FunctionCalling
   :noindex:

   An **event** class representing a single function invocation. It tracks:

   - **Which tool** to call (:attr:`func_tool`).
   - **Arguments** to pass (:attr:`arguments`).
   - **Execution** metadata (duration, status, response, error) via
     :attr:`execution`.

   **Methods**:

   .. method:: invoke() -> None
      :async:

      1. Optionally run :attr:`func_tool.preprocessor` on :attr:`arguments`.
      2. Call the function (``await`` if async).
      3. Optionally run :attr:`func_tool.postprocessor` on the result.
      4. Set the execution status to COMPLETED or FAILED, plus store
         the output or error message.

   **Usage Example**::

      from lionagi.action.function_calling import FunctionCalling
      from lionagi.action.tool import Tool

      def greet(name: str) -> str:
          return f"Hello, {name}!"

      tool = Tool(greet)
      call_event = FunctionCalling(func_tool=tool, arguments={"name": "Alice"})

      # In an async context:
      await call_event.invoke()
      print(call_event.execution.response)  # "Hello, Alice!"
      print(call_event.status)              # COMPLETED


ActionRequestModel
~~~~~~~~~~~~~~~~~
.. class:: ActionRequestModel
   :noindex:

   Pydantic model that describes a requested function call. Typically used
   to parse inbound data that specifies which function to call and what
   arguments to provide.

   **Fields**:

   .. py:attribute:: function
      :type: str | None

      The name of the function/tool to invoke. If None, no function is selected.

   .. py:attribute:: arguments
      :type: dict[str, Any] | None

      The dictionary of arguments for the function call.

   **Class Methods**:

   .. method:: create(content: str) -> list[ActionRequestModel]

      Attempts to parse a JSON string (or similar) into one or more
      :class:`ActionRequestModel` objects. Returns an empty list on failure.


ActionResponseModel
~~~~~~~~~~~~~~~~~~
.. class:: ActionResponseModel
   :noindex:

   Pydantic model describing the **result** of a function call. Includes:

   - :attr:`function`: The function name.
   - :attr:`arguments`: The passed arguments.
   - :attr:`output`: The function's return value, if any.


ActionManager
~~~~~~~~~~~~~
.. class:: ActionManager
   :noindex:

   The **central registry** for function tools. You can register Python callables
   (or pre-wrapped :class:`Tool` objects) and invoke them by name with the correct
   arguments.

   **Core Usage**:

   1) Instantiate :class:`ActionManager`.

   2) Use :meth:`register_tool` or :meth:`register_tools` to add functions.

   3) Call :meth:`invoke` with a dictionary or :class:`ActionRequestModel` specifying
   ``{"function": "...", "arguments": {...}}``.

   Under the hood, :meth:`invoke` creates a :class:`FunctionCalling` event and
   runs :meth:`FunctionCalling.invoke`. The final or error outcome is contained
   in the event's execution.

   **Key Methods**:

   .. method:: __init__(*args, **kwargs)

      Collect any tools provided via args/kwargs and register them.

   .. method:: register_tool(tool: FuncTool, update: bool = False) -> None

      Register a single function or :class:`Tool`. If the function name is already
      taken and ``update=False``, raises ``ValueError``.

   .. method:: register_tools(tools: list[FuncTool] | FuncTool, update: bool = False) -> None

      Register multiple functions or tools at once.

   .. method:: invoke(func_call: ActionRequestModel | dict) -> FunctionCalling | None
      :async:

      Matches the function name, builds a :class:`FunctionCalling`, invokes it,
      and returns the event (or logs an error). The event’s :attr:`execution` tracks
      success/failure.

      **Example**::

         from lionagi.action.manager import ActionManager

         manager = ActionManager()

         def multiply(a: int, b: int) -> int:
             return a * b

         manager.register_tool(multiply)
         req = {"function": "multiply", "arguments": {"a": 3, "b": 5}}

         result = await manager.invoke(req)
         print(result.execution.response)  # 15


----------------------------
Integration with Event System
----------------------------
Because **FunctionCalling** can inherit from :class:`~lionagi.protocols.types.Event`, it
may be queued or stored in LionAGI's concurrency structures. For instance, you could:

1. Create a :class:`FunctionCalling` event for each function call you need.
2. Add these events to a :class:`~lionagi.protocols.generic.processor.Executor`, which
   uses a :class:`~lionagi.protocols.generic.processor.Processor` to manage concurrency.
3. The events might be stored in a :class:`~lionagi.protocols.generic.pile.Pile` and
   ordered by a :class:`~lionagi.protocols.generic.progression.Progression`.
4. As the Processor runs, it calls :meth:`FunctionCalling.invoke()` for each event,
   gathering results or errors in the :attr:`execution` field.

This unifies local function calls under LionAGI’s broader **event-driven** design,
ensuring consistent logging, status tracking, and integration with other event types
(like advanced scheduling).

-----------------
Additional Examples
-----------------

**Strict Validation**:

If ``strict_func_call=True`` on a :class:`Tool`, the arguments **must** match the
function's signature exactly. Any extra or missing parameters raise a
``ValueError``:

.. code-block:: python

   from lionagi.action.tool import Tool

   def greet(person: str, punctuation: str = "!") -> str:
       return f"Hello, {person}{punctuation}"

   greet_tool = Tool(
       func_callable=greet,
       strict_func_call=True
   )

   # This fails if 'punctuation' is missing but required, or if you add any unknown keys.

**Pre/Post Processing**:

You can attach a preprocessor and postprocessor to the :class:`Tool`:

.. code-block:: python

   def pre_check(args, **kwargs):
       if args.get("x", 0) < 0:
           raise ValueError("x must be >= 0")
       return args

   def format_result(result, **kwargs):
       return f"Computed: {result}"

   from lionagi.action.tool import Tool

   def add(x: int, y: int) -> int:
       return x + y

   add_tool = Tool(
       func_callable=add,
       preprocessor=pre_check,
       postprocessor=format_result
   )

   # The final result in FunctionCalling.execution.response will be "Computed: <int>"
