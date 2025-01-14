.. _lionagi-action-system:

================================================
Action System
================================================

Overview
--------
The **action** system enables **function calling** within LionAGI:

- **Tools** wrap a Python callable with optional pre/post processors and schema-based validation.
- **FunctionCalling** is a specialized `Event` that executes these tools.
- **ActionManager** registers multiple Tools for invocation by requests.
- **ActionRequestModel** and **ActionResponseModel** define standardized protocols
  for specifying which function to call, with what arguments, and returning the function's output.

Contents
--------
.. contents::
   :local:
   :depth: 2


FunctionCalling
---------------

The :class:`FunctionCalling` class extends :class:`~lionagi.protocols.generic.event.Event`
to manage the entire lifecycle of a **tool** invocation, including optional
pre and post processing. It updates :attr:`execution` with status, duration,
and any output or error.

Class Documentation
^^^^^^^^^^^^^^^^^

.. class:: FunctionCalling
   :module: lionagi.operatives.action.function_calling

   **Inherits from**: :class:`~lionagi.protocols.generic.event.Event`

   Handles asynchronous function execution with pre/post processing.
    This class manages function calls with optional preprocessing and
    postprocessing, handling both synchronous and asynchronous functions.

    Attributes
    ----------
    func_tool : Tool
        Tool instance containing the function to be called
    arguments : dict[str, Any]
        Dictionary of arguments to pass to the function
    
    Methods
    -------
    invoke()
        Execute the function call with pre/post processing.
    to_dict()
        Convert instance to dictionary.

    Properties
    ----------
    function
        Returns the underlying function from func_tool.

    Examples
    --------
    >>> def multiply(x, y):
    ...     return x * y
    >>> tool = Tool(func_callable=multiply)
    >>> func_call = FunctionCalling(func_tool=tool, arguments={"x": 3, "y": 4})
    >>> await func_call.invoke()
    >>> print(func_call.execution.response)  # Should show 12

Method Documentation
^^^^^^^^^^^^^^^^^^

.. method:: FunctionCalling.invoke()

    Execute the function call with pre/post processing.

    Handles both synchronous and asynchronous functions, including optional
    preprocessing of arguments and postprocessing of results. Updates the
    execution status, duration, and response/error.

    Returns
    -------
    None

.. method:: FunctionCalling.to_dict()

    Convert instance to dictionary.

    Returns
    -------
    dict[str, Any]
        Dictionary representation of the instance including function name
        and arguments.


ActionManager
-------------

A specialized :class:`~lionagi.protocols._concepts.Manager` that keeps a
registry of **tools** (functions). It also provides an `invoke` method for
easily executing a registered function, given an :class:`ActionRequest` or
its Pydantic model.

Class Documentation
^^^^^^^^^^^^^^^^^

.. class:: ActionManager
   :module: lionagi.operatives.action.manager

   **Inherits from**: :class:`~lionagi.protocols._concepts.Manager`

   A manager that registers function-based tools and invokes them
    when triggered by an ActionRequest. Tools can be registered
    individually or in bulk, and each tool must have a unique name.

    Parameters
    ----------
    *args : FuncTool
        A variable number of tools or callables.
    **kwargs
        Additional named arguments that are also considered tools.

    Attributes
    ----------
    registry : dict[str, Tool]
        Dictionary mapping function names to Tool instances.

    Methods
    -------
    register_tool(tool, update=False)
        Register a single tool/callable in the manager.
    register_tools(tools, update=False)
        Register multiple tools at once.
    match_tool(action_request)
        Convert an ActionRequest into a FunctionCalling instance.
    invoke(func_call)
        High-level API to parse and run a function call.
    get_tool_schema(tools=False, auto_register=True, update=False)
        Retrieve schemas for a subset of tools or for all.

    Properties
    ----------
    schema_list
        Return the list of JSON schemas for all registered tools.

Method Documentation
^^^^^^^^^^^^^^^^^^

.. method:: ActionManager.register_tool(tool, update=False)

    Register a single tool/callable in the manager.

    Parameters
    ----------
    tool : FuncTool
        A `Tool` object or a raw callable function.
    update : bool, default=False
        If True, allow replacing an existing tool with the same name.

    Raises
    ------
    ValueError
        If tool already registered and update=False.
    TypeError
        If `tool` is not a Tool or callable.

.. method:: ActionManager.register_tools(tools, update=False)

    Register multiple tools at once.

    Parameters
    ----------
    tools : list[FuncTool] | FuncTool
        A single or list of tools/callables.
    update : bool, default=False
        If True, allow updating existing tools.

    Raises
    ------
    ValueError
        If a duplicate tool is found and update=False.
    TypeError
        If any item is not a Tool or callable.

.. method:: ActionManager.match_tool(action_request)

    Convert an ActionRequest (or dict with "function"/"arguments")
    into a `FunctionCalling` instance by finding the matching tool.

    Parameters
    ----------
    action_request : ActionRequest | ActionRequestModel | dict
        The request specifying which function to call and with what arguments.

    Returns
    -------
    FunctionCalling
        The event object that can be invoked.

    Raises
    ------
    TypeError
        If `action_request` is an unsupported type.
    ValueError
        If no matching tool is found in the registry.

.. method:: ActionManager.invoke(func_call)

    High-level API to parse and run a function call.

    Steps:
      1) Convert `func_call` to FunctionCalling via `match_tool`.
      2) `invoke()` the resulting object.
      3) Return the `FunctionCalling`, which includes `execution`.

    Parameters
    ----------
    func_call : ActionRequestModel | ActionRequest
        The action request model or ActionRequest object.

    Returns
    -------
    FunctionCalling
        The event object after execution completes.

.. method:: ActionManager.get_tool_schema(tools=False, auto_register=True, update=False)

    Retrieve schemas for a subset of tools or for all.

    Parameters
    ----------
    tools : ToolRef, default=False
        - If True, return schema for all tools.
        - If False, return an empty dict.
        - If specific tool(s), returns only those schemas.
    auto_register : bool, default=True
        If a tool (callable) is not yet in the registry, register if True.
    update : bool, default=False
        If True, allow updating existing tools.

    Returns
    -------
    dict
        Dictionary containing tool schemas, e.g., {"tools": [list of schemas]}

    Raises
    ------
    ValueError
        If requested tool is not found and auto_register=False.
    TypeError
        If tool specification is invalid.


Request & Response Models
-------------------------

Contains Pydantic models for action requests and responses. These models typically map
to conversation messages describing which function is called, with what arguments,
and any returned output.

Class Documentation
^^^^^^^^^^^^^^^^^

.. class:: ActionRequestModel
   :module: lionagi.operatives.action.request_response_model

   **Inherits from**: :class:`pydantic.BaseModel`

   Captures a single action request.
    Includes the name of the function and the arguments.

    Attributes
    ----------
    function : str | None
        Name of the function to call (e.g., "multiply", "create_user")
    arguments : dict[str, Any] | None
        Dictionary of arguments to pass to the function

    Methods
    -------
    create(content)
        Class method to parse a string into one or more ActionRequestModel instances.

    Examples
    --------
    >>> request = ActionRequestModel(
    ...     function="multiply",
    ...     arguments={"x": 3, "y": 4}
    ... )

Method Documentation
^^^^^^^^^^^^^^^^^^

.. method:: ActionRequestModel.create(content)

    Attempt to parse a string (usually from a conversation or JSON) into
    one or more ActionRequestModel instances.

    Parameters
    ----------
    content : str
        String content to parse.

    Returns
    -------
    list[ActionRequestModel]
        List of parsed request models. Returns empty list if no valid structure found.

.. class:: ActionResponseModel
   :module: lionagi.operatives.action.request_response_model

   **Inherits from**: :class:`pydantic.BaseModel`

   Encapsulates a function's output after being called. Typically
    references the original function name, arguments, and the result.

    Attributes
    ----------
    function : str
        Name of the function that was called
    arguments : dict[str, Any]
        Dictionary of arguments that were passed
    output : Any
        The function's return value or output

    Examples
    --------
    >>> response = ActionResponseModel(
    ...     function="multiply",
    ...     arguments={"x": 3, "y": 4},
    ...     output=12
    ... )

Field Models
^^^^^^^^^^^

The module also defines two field models for use in other Pydantic models:

- ``ACTION_REQUESTS_FIELD``: For lists of action requests
- ``ACTION_RESPONSES_FIELD``: For lists of action responses


Tool
----

The Tool module provides functionality for wrapping Python callables with additional
features like pre/post-processing and automatic schema generation.

Class Documentation
^^^^^^^^^^^^^^^^^

.. class:: Tool
   :module: lionagi.operatives.action.tool

   **Inherits from**: :class:`pydantic.BaseModel`

   Wraps a callable function with optional preprocessing of arguments,
    postprocessing of results, and strict or partial argument matching.
    The tool_schema is auto-generated from the function signature if not provided.

    Parameters
    ----------
    func_callable : Callable[..., Any]
        The callable function to be wrapped by the tool
    tool_schema : dict[str, Any] | None, optional
        Schema describing the function's parameters and structure
    preprocessor : Callable[[Any], Any] | None, optional
        Optional function for preprocessing inputs before execution
    preprocessor_kwargs : dict[str, Any], optional
        Keyword arguments passed to the preprocessor function
    postprocessor : Callable[[Any], Any] | None, optional
        Optional function for postprocessing outputs after execution
    postprocessor_kwargs : dict[str, Any], optional
        Keyword arguments passed to the postprocessor function
    strict_func_call : bool, default=False
        Whether to enforce strict validation of function parameters

    Properties
    ----------
    function : str
        Return the function name from the auto-generated schema
    required_fields : set[str]
        Return the set of required parameter names from the schema
    minimum_acceptable_fields : set[str]
        Return the set of parameters that have no default values

    Methods
    -------
    to_dict()
        Serialize the Tool to a dict, including the function name

Type Aliases
^^^^^^^^^^^

.. data:: FuncTool

    Type alias representing either a `Tool` instance or a raw callable function.
    ``Tool | Callable[..., Any]``

.. data:: FuncToolRef

    Type alias for a reference to a function-based tool, by either the actual object,
    the raw callable, or the function name as a string.
    ``FuncTool | str``

.. data:: ToolRef

    Type alias used for specifying one or more tool references, or a boolean
    indicating 'all' or 'none'.
    ``FuncToolRef | list[FuncToolRef] | bool``

Helper Functions
^^^^^^^^^^^^^^

.. function:: func_to_tool(func, **kwargs)

    Convenience function that wraps a raw function in a `Tool`.

    Parameters
    ----------
    func : Callable[..., Any]
        The function to wrap
    **kwargs
        Additional arguments passed to the `Tool` constructor

    Returns
    -------
    Tool
        A new Tool instance wrapping `func`

Examples
^^^^^^^^

.. code-block:: python

    def greet(name: str, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}!"

    # Basic tool creation
    tool = Tool(func_callable=greet)

    # With preprocessing
    def preprocess(args):
        args["name"] = args["name"].title()
        return args

    tool_with_prep = Tool(
        func_callable=greet,
        preprocessor=preprocess,
        strict_func_call=True
    )

Utilities
---------

Internal helpers for parsing action requests and validating fields.

Functions
^^^^^^^^

.. function:: parse_action_request(content)

    Attempt to parse a string or dictionary into a list of action request
    dictionaries. Handles various input formats including JSON strings,
    Python code blocks, and dictionaries.

    Parameters
    ----------
    content : str | dict
        The content to parse, either as a string or dictionary.

    Returns
    -------
    list[dict]
        List of dictionaries, each containing 'function' and 'arguments' keys.

Field Models
^^^^^^^^^^^

.. data:: FUNCTION_FIELD

    Field model for function names with validation.

    Attributes
    ----------
    name : str
        "function"
    default : None
        Default value is None
    annotation : str | None
        Type annotation
    description : str
        Description of how to use the function field
    examples : list
        Example function names like ["add", "multiply", "divide"]

.. data:: ARGUMENTS_FIELD

    Field model for function arguments with validation.

    Attributes
    ----------
    name : str
        "arguments"
    default_factory : dict
        Default value is an empty dict
    annotation : dict | None
        Type annotation
    description : str
        Description of how to use the arguments field
    examples : list
        Example argument dictionaries

.. data:: ACTION_REQUIRED_FIELD

    Field model indicating whether actions are required.

    Attributes
    ----------
    name : str
        "action_required"
    default : bool
        Default value is False
    annotation : bool
        Type annotation
    description : str
        Description of when actions are required vs optional

Field Descriptions
^^^^^^^^^^^^^^^^^

The module provides several constant strings describing fields:

- ``function_field_description``: Guidelines for function name field
- ``arguments_field_description``: Guidelines for arguments field
- ``action_required_field_description``: Guidelines for required flag
- ``action_requests_field_description``: Guidelines for request lists


Example Usage
-------------
A short example of how to use these classes:

.. code-block:: python

   from lionagi.operatives.action.manager import ActionManager
   from lionagi.operatives.action.request_response_model import ActionRequestModel

   # 1. Create an action manager and register a function
   def multiply(x, y):
       return x * y

   manager = ActionManager()
   manager.register_tool(multiply)

   # 2. Build an ActionRequestModel
   request_data = {"function": "multiply", "arguments": {"x": 3, "y": 4}}
   action_request = ActionRequestModel.model_validate(request_data)

   # 3. Invoke
   result_event = await manager.invoke(action_request)
   print(result_event.execution.response)  # Should show 12


File Locations
--------------
- **function_calling.py**: 
  The :class:`FunctionCalling` event for executing tools.

- **manager.py** (ActionManager): 
  The main manager for registering and invoking Tools.

- **request_response_model.py**: 
  Pydantic-based models for requests/responses.

- **tool.py**: 
  The :class:`Tool` class that wraps a callable function with schema info.

- **utils.py**: 
  Shared utility constants and a simple parser method for requests.

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
