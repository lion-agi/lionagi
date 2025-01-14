.. _lionagi-messages:

====================================================
Messages Subsystem
====================================================
.. module:: lionagi.protocols.messages
   :synopsis: Classes for instructions, AI responses, action requests/responses, and system-level messages.

Overview
--------
This subsystem handles **structured messages** in LionAGI, enabling:
- **User instructions** (with context, images, or tool references),
- **System** messages that define context or constraints,
- **Assistant** responses capturing AI output,
- **ActionRequests** and **ActionResponses** to call code or tools.

All are subclasses of :class:`RoledMessage`, which defines a *role*, *sender*, *recipient*, and *content*.

Contents
--------
.. contents::
   :local:
   :depth: 2


Base Types
----------
.. _lionagi-messages-base:

.. automodule:: lionagi.protocols.messages.base
   :members:
   :undoc-members:
   :show-inheritance:

Key enumerations like :class:`MessageRole` (``SYSTEM``, ``USER``, 
``ASSISTANT``, etc.) and the basic notion of a “sender/recipient” 
reside here.


RoledMessage
------------
.. _lionagi-messages-message:

.. automodule:: lionagi.protocols.messages.message
   :members:
   :undoc-members:
   :show-inheritance:

Defines a general base class for typed messages with a **role**. 
Every specialized message (like system instructions, user instructions, 
or AI responses) inherits from :class:`RoledMessage`.


System
------
.. automodule:: lionagi.protocols.messages.system
   :members:
   :undoc-members:
   :show-inheritance:

:class:`System` sets *system-level* instructions. Typically the 
very first message in a conversation, it describes how the AI 
should behave overall.


Instruction
-----------
.. automodule:: lionagi.protocols.messages.instruction
   :members:
   :undoc-members:
   :show-inheritance:

:class:`Instruction` captures the **user's** command or question. 
It may contain optional context or images, as well as a schema 
for structured responses.


AssistantResponse
-----------------
.. automodule:: lionagi.protocols.messages.assistant_response
   :members:
   :undoc-members:
   :show-inheritance:

:class:`AssistantResponse` is the AI's reply to a user or system 
message. This may store raw model data (JSON output) in 
``metadata["model_response"]``.


ActionRequest
-------------
.. automodule:: lionagi.protocols.messages.action_request
   :members:
   :undoc-members:
   :show-inheritance:

:class:`ActionRequest` is a special message for requesting a 
function call or action. Contains a function name and arguments.


ActionResponse
--------------
.. automodule:: lionagi.protocols.messages.action_response
   :members:
   :undoc-members:
   :show-inheritance:

Pairs with an :class:`ActionRequest`, providing the **output** 
of that requested function. The original request ID is also tracked.


MessageManager
--------------
.. automodule:: lionagi.protocols.messages.manager
   :members:
   :undoc-members:
   :show-inheritance:

A manager for collecting messages in order, offering utility methods 
to add system instructions, user instructions, or assistant responses, 
and to fetch them (e.g. “last instruction”). Also includes 
**action** request/response handling.


Example Usage
-------------
.. code-block:: python

   from lionagi.protocols.messages.message_manager import MessageManager
   from lionagi.protocols.messages.system import System
   from lionagi.protocols.messages.instruction import Instruction
   from lionagi.protocols.messages.assistant_response import AssistantResponse

   # 1) Create a manager
   manager = MessageManager(system=System.create())

   # 2) Add a user instruction
   instruct = Instruction.create(instruction="How to deploy a python app?")
   msg, _ = manager.add_message(instruction=instruct)
   
   # 3) AI responds
   response = AssistantResponse.create("You can use Docker or a PaaS like Heroku.")
   msg, _ = manager.add_message(assistant_response=response)

   # Inspect
   print(manager.last_response.response)
   # -> "You can use Docker or a PaaS like Heroku."


File Locations
--------------
- **base.py**: Shared role/flag definitions.  
- **message.py**: The :class:`RoledMessage` base class + jinja environment.  
- **system.py**: The :class:`System` specialized message.  
- **instruction.py**: The :class:`Instruction` specialized message.  
- **assistant_response.py**: The :class:`AssistantResponse` specialized message.  
- **action_request.py**: The :class:`ActionRequest` specialized message.  
- **action_response.py**: The :class:`ActionResponse` specialized message.  
- **message_manager.py**: A manager class for storing and operating on multiple messages.

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
