=============================================
Messages & Conversation
=============================================

This document provides an overview of LionAGI’s **message system**, which
supports structured, multi-turn conversations, user instructions, and
action requests/responses. Each message class (e.g., ``System``, ``Instruction``,
``ActionRequest``, ``ActionResponse``, ``AssistantResponse``) inherits
from a shared base (:class:`RoledMessage`), itself extending LionAGI’s
:class:`Element`. This design ensures each message has a unique UUID,
metadata, and can be integrated with concurrency/event structures (like
a :class:`~lionagi.protocols.generic.pile.Pile` or
:class:`~lionagi.protocols.generic.processor.Executor`).



---------------------
1. Core Architecture
---------------------

Each **message class** in this subsystem inherits (directly or indirectly) from:

1. **:class:`Element`**  
   Provides a UUID-based identifier (:attr:`id`), creation timestamp
   (:attr:`created_at`), and a metadata dict for custom fields.

2. **:class:`RoledMessage`** (defined in ``message.py``)  
   Adds conversation-specific attributes:
   - :attr:`role` (e.g., ``SYSTEM``, ``USER``, ``ASSISTANT``, ``ACTION``)
   - :attr:`content` (a dictionary of data)
   - Optional :attr:`template` (for rendering text).  
   Also implements :class:`~lionagi.protocols._concepts.Sendable`—allowing
   each message to specify ``sender`` and ``recipient`` as roles, strings,
   or other Elements.


----------------------------
2. High-Level Message Classes
----------------------------

System
~~~~~~
.. class:: System
   :module: lionagi.protocols.messages.system

   A message containing **system-level** instructions, typically the first 
   in a conversation. Always has the role :attr:`MessageRole.SYSTEM`.
   
   - **Purpose**: Provide high-level policies, guidelines, or style instructions 
     for the AI (e.g., “You are a helpful AI assistant”).
   - **Key Fields**:
     
     .. attribute:: system_message
        The main text or guidance.

     .. attribute:: system_datetime
        Optional timestamp or user-provided time string embedded in the content.

   **Example**::

      from lionagi.protocols.messages.system import System

      sys_msg = System.create(
          system_message="You are a helpful AI assistant. Let's think step by step."
      )
      print(sys_msg.content["system_message"])
      # => "You are a helpful AI assistant. Let's think step by step."


Instruction
~~~~~~~~~~~
.. class:: Instruction
   :module: lionagi.protocols.messages.instruction

   Represents a **user’s prompt** or request, typically with the role
   :attr:`MessageRole.USER`. May contain:

   - **Guidance** or **context** (e.g., background knowledge).
   - **Images** or references to images.
   - **Schemas** describing how the AI should respond (e.g., `request_model`).
   - **Plain content** or structured fields.

   **Notable methods/fields**:

   - :meth:`create()`: Build an ``Instruction`` with fields like
     ``instruction``, ``context``, ``images``, etc.
   - :meth:`rendered`: Returns a final textual/structured representation.

   **Example**::

      from lionagi.protocols.messages.instruction import Instruction

      inst = Instruction.create(
          instruction="How do I parse JSON in Python?",
          context=["Some additional context..."]
      )
      print(inst.instruction)
      # => "How do I parse JSON in Python?"


ActionRequest
~~~~~~~~~~~~~
.. class:: ActionRequest
   :module: lionagi.protocols.messages.action_request

   Specialized message for requesting a function or “tool” invocation. 
   Has the role :attr:`MessageRole.ACTION`.  
   Typical usage:
   
   1. **function**: The name (or reference) of the function to be called.
   2. **arguments**: A dictionary of parameters.

   Pairs with :class:`ActionResponse` to capture results. Often used within
   LionAGI’s :class:`ActionManager` or from user input desiring a function call.

   **Example**::

      from lionagi.protocols.messages.action_request import ActionRequest

      request_msg = ActionRequest.create(
          function="add",
          arguments={"x": 10, "y": 5},
      )
      print(request_msg.function)    # => "add"
      print(request_msg.arguments)   # => {"x": 10, "y": 5}


ActionResponse
~~~~~~~~~~~~~~
.. class:: ActionResponse
   :module: lionagi.protocols.messages.action_response

   The counterpart to :class:`ActionRequest`. Also has the role
   :attr:`MessageRole.ACTION`, but stores:

   - **function** and **arguments**: Echoing the request.
   - **output**: The final result of the function/tool call.

   Typically created after an action is executed, linking back to the
   :attr:`action_request_id` to indicate which request triggered it.

   **Example**::

      from lionagi.protocols.messages.action_response import ActionResponse
      from lionagi.protocols.messages.action_request import ActionRequest

      req = ActionRequest.create(
          function="add",
          arguments={"x": 2, "y": 3}
      )
      resp = ActionResponse.create(
          action_request=req,
          output=5
      )
      print(resp.output)  # => 5


AssistantResponse
~~~~~~~~~~~~~~~~
.. class:: AssistantResponse
   :module: lionagi.protocols.messages.assistant_response

   Represents the **AI assistant’s reply** (role :attr:`MessageRole.ASSISTANT`).
   Can store:

   - A final user-facing text in :attr:`assistant_response`.
   - Raw model data in :attr:`model_response` (e.g., an OpenAI ChatCompletion
     JSON).

   **Example**::

      from lionagi.protocols.messages.assistant_response import AssistantResponse

      aresp = AssistantResponse.create(
          assistant_response="Here is your answer..."
      )
      print(aresp.response)  # => "Here is your answer..."


-----------------------
3. MessageManager
-----------------------
.. class:: MessageManager
   :module: lionagi.protocols.messages.manager

   A **container** for storing multiple messages in a chronological or
   logical :class:`~lionagi.protocols.generic.progression.Progression`.
   Internally uses a :class:`~lionagi.protocols.generic.pile.Pile` to manage
   insertion order, concurrency, etc.

   **Capabilities**:
   
   - **Adding messages**: via :meth:`add_message`, specifying 
     system/instruction/action_request/etc.
   - Maintaining a dedicated **system** message (the first message).
   - Properties to retrieve **last_instruction**, **assistant_responses**, etc.
   - :meth:`to_chat_msgs()` yields a list of messages in a format 
     suitable for a standard chat interface (``[{"role":..., "content":...}]``).

   **Code Example**::

      from lionagi.protocols.messages.manager import MessageManager
      from lionagi.protocols.messages.system import System

      msg_manager = MessageManager()
      sys_msg = System.create(system_message="System: be polite, etc.")
      msg_manager.add_message(system=sys_msg)

      # Add user instruction
      msg_manager.add_message(instruction="Hello, how are you?")

      # Add assistant response
      msg_manager.add_message(assistant_response="I'm well, thanks for asking.")

      # Retrieve everything in chat format
      chat_history = msg_manager.to_chat_msgs()
      for msg in chat_history:
          print(msg["role"], "->", msg["content"])


------------------
4. Common Patterns
------------------
1. **Creating/Updating a Message**  
   Each message class has a :meth:`create` method to produce a new instance
   from constructor arguments. Some also provide :meth:`update` to revise
   the message’s existing content while preserving its UUID.

2. **Using with Concurrency**  
   Because these messages inherit from :class:`Element`, they can be placed
   in a :class:`~lionagi.protocols.generic.pile.Pile` or scheduled in a
   :class:`~lionagi.protocols.generic.processor.Executor`.  
   Action-related messages (``ActionRequest``, ``ActionResponse``) can 
   also link to :class:`~lionagi.action.function_calling.FunctionCalling`
   events for tool invocation.

3. **Connecting Request/Response**  
   - An :class:`ActionRequest` references a function plus arguments.
   - On completion, an :class:`ActionResponse` is created with the same function
     name/arguments, plus an :attr:`output`.
   - The original request can track if it’s responded to by checking
     :attr:`action_response_id`.

4. **Rendering**  
   :class:`RoledMessage` optionally uses a Jinja2 :attr:`template` for 
   generating a textual representation of :attr:`content`. If no template
   is set, a default JSON serialization is used.

5. **System vs. Instruction**  
   - **System** messages typically come first in a conversation, establishing
     AI policy or style.
   - **Instruction** messages correspond to the user’s primary query or request.
   - **AssistantResponse** messages hold the AI’s reply.

-----------------------
5. Putting It All Together
-----------------------
Below is a mini example showing how these pieces fit into a conversation:

.. code-block:: python

   from lionagi.protocols.messages.system import System
   from lionagi.protocols.messages.instruction import Instruction
   from lionagi.protocols.messages.assistant_response import AssistantResponse
   from lionagi.protocols.messages.manager import MessageManager

   # 1) Create a MessageManager
   manager = MessageManager()

   # 2) Set a System message
   sys_msg = System.create(system_message="You are a math assistant. Please be accurate.")
   manager.add_message(system=sys_msg)

   # 3) The user sends an Instruction
   manager.add_message(instruction="Calculate 12 * 8, please.")

   # 4) The assistant responds
   manager.add_message(assistant_response="The result is 96.")

   # 5) Display the chat structure
   for msg_dict in manager.to_chat_msgs():
       print(msg_dict["role"], "->", msg_dict["content"])


With these message classes, LionAGI can handle:

- **System** instructions that shape AI behavior.
- **User** instructions with optional advanced formats (images, schemas, etc.).
- **Actions** for function calls (via :class:`ActionRequest` and 
  :class:`ActionResponse`).
- **Assistant** replies with final or intermediate results.

Ultimately, this messages subsystem ensures each portion of a conversation
or action request is neatly stored, typed, and logged, facilitating 
both *multi-turn dialogs* and *tool-usage flows*.
