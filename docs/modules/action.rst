.. _lionagi-action-system:

================================================
Action System
================================================
.. module:: lionagi.operatives.action
   :synopsis: Tools, requests, and managers for function-based actions.

Overview
--------
The **action** system enables **function calling** within LionAGI:

- **Tools** wrap a Python callable with optional pre/post processors and schema-based validation.
- **FunctionCalling** is a specialized `Event` that executes these tools.
- **ActionManager** registers multiple Tools for invocation by requests.
- **ActionRequestModel** and **ActionResponseModel** define standardized message formats
  for specifying which function to call, with what arguments, and returning the function's output.

Contents
--------
.. contents::
   :local:
   :depth: 2


FunctionCalling
---------------
.. automodule:: lionagi.operatives.action.function_calling
   :members:
   :undoc-members:
   :show-inheritance:

   The :class:`FunctionCalling` class extends :class:`~lionagi.protocols.generic.event.Event`
   to manage the entire lifecycle of a **tool** invocation, including optional
   pre and post processing. It updates :attr:`execution` with status, duration,
   and any output or error.


ActionManager
-------------
.. automodule:: lionagi.operatives.action.manager
   :members:
   :undoc-members:
   :show-inheritance:

   A specialized :class:`~lionagi.protocols._concepts.Manager` that keeps a
   registry of **tools** (functions). It also provides an `invoke` method for
   easily executing a registered function, given an :class:`ActionRequest` or
   its Pydantic model.


Request & Response Models
-------------------------
.. automodule:: lionagi.operatives.action.request_response_model
   :members:
   :undoc-members:
   :show-inheritance:

   Contains pydantic classes:
   - :class:`ActionRequestModel`: For specifying `function` and `arguments`.
   - :class:`ActionResponseModel`: For indicating the function output.


Tool
----
.. automodule:: lionagi.operatives.action.tool
   :members:
   :undoc-members:
   :show-inheritance:

   Defines :class:`Tool`, which wraps a Python callable and auto-generates a JSON schema
   describing its parameters. Also includes type aliases like ``FuncTool``.

Utilities
---------
.. automodule:: lionagi.operatives.action.utils
   :members:
   :undoc-members:

   Internal helpers, including constants for field descriptions and the
   function `parse_action_request` for parsing a JSON string into a list
   of requests.


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
