.. _lionagi-branch-operations:

=================================================
Branch-Level Operations
=================================================
These operations define how a :class:`~lionagi.session.branch.Branch` 
actually **does** things—ranging from direct LLM calls (`chat`, `communicate`) 
to advanced flows (`operate`, `instruct`, `interpret`, `ReAct`, etc.). Each 
is implemented as a separate function and exposed as an **asynchronous** 
method on ``Branch``.

For convenience, they can be categorized as:

- **Simple conversation**: :func:`chat`, :func:`communicate`
- **Structured conversation**: :func:`operate`, :func:`instruct`
- **Short or specialized**: :func:`interpret`, :func:`translate`
- **Action invocation**: :func:`_act`, :func:`act`
- **Selection**: :func:`select`
- **ReAct**: :func:`ReAct` for multi-step reasoning
- **Parsing**: :func:`parse` to convert text to a structured model


``_act``
--------
.. autofunction:: lionagi.operations._act.act._act

   A **low-level** method invoked by :meth:`branch.act()`. It matches an 
   action request (function + arguments) to the :class:`ActionManager` 
   and executes it, returning an :class:`ActionResponse`. Typically 
   you won't call ``_act`` directly; use :meth:`act` instead.


``act``
-------
.. automethod:: lionagi.session.branch.Branch.act

   The *public* interface for invoking tools. Accepts a single or list 
   of action requests. Optionally retries, logs errors, or merges results. 
   This is best used for **explicit function calls** triggered from user 
   instructions or system logic.


``chat``
--------
.. automethod:: lionagi.session.branch.Branch.chat

   The fundamental LLM-based conversation method. Combines existing 
   messages with a new instruction (and optional guidance/context) 
   into a single prompt, sends it to the chat model, and returns 
   the final :class:`AssistantResponse`. It can also produce an 
   :class:`Instruction` if you set certain flags.


``communicate``
---------------
.. automethod:: lionagi.session.branch.Branch.communicate

   Similar to :meth:`chat`, but typically used for simpler calls 
   that automatically add the user query and model response to 
   the conversation. It also supports optional validation into 
   a Pydantic model or partial “request_fields” extraction. 
   If you do not need advanced flows like action calls, 
   :meth:`communicate` is a good, straightforward choice.


``operate``
-----------
.. automethod:: lionagi.session.branch.Branch.operate

   A **robust** conversation operation that merges user instructions 
   with an internal “Operative” object for structured input and output. 
   It can also automatically detect requested tool calls and run them, 
   then re-check or finalize the LLM output. Often used in more 
   advanced scenarios where you want strong parsing or multiple 
   sub-steps in the final result.


``parse``
---------
.. automethod:: lionagi.session.branch.Branch.parse

   A dedicated method for parsing raw text into a 
   :class:`pydantic.BaseModel` if you do not want to incorporate 
   it in the main conversation flow. Supports fuzzy matching, 
   custom field handling, etc.


``instruct``
------------
.. automethod:: lionagi.session.branch.Branch.instruct

   Provides a **mid-level** approach: if your user instructions 
   (wrapped in :class:`Instruct`) indicate advanced features 
   (like actions, or a custom structured response), 
   it calls :meth:`operate` internally. Otherwise, 
   it calls :meth:`communicate`. Best for single-turn instructions 
   that may or may not trigger advanced logic.


``interpret``
-------------
.. automethod:: lionagi.session.branch.Branch.interpret

   Rewrites or refines user input into a more structured, 
   explicit prompt. Useful if the user's original text might 
   be ambiguous or suboptimal for the LLM. It does not store 
   messages into the conversation by default.


``ReAct``
---------
.. automethod:: lionagi.session.branch.Branch.ReAct

   Implements a multi-step “**reason + act**” approach, where 
   the LLM is asked for chain-of-thought or intermediate steps 
   that might require additional expansions. Once the chain-of-thought 
   is complete, a final answer is produced. 
   Optionally repeats expansions if “extension_needed” is signaled, 
   up to a specified limit. Typically used in complex tasks.


``select``
----------
.. automethod:: lionagi.session.branch.Branch.select

   A convenience operation for letting the LLM choose one or more 
   items from a given list or dictionary. For instance, if you have 
   10 possible solutions and want the model to pick the best one(s). 
   Returns a structured “selection model” describing which was chosen.


``translate``
-------------
.. automethod:: lionagi.session.branch.Branch.translate

   A specialized method for transforming text with a given 
   “technique” (currently “SynthLang”), optionally compressing 
   the result. This is a demonstration of hooking up 
   domain-specific transformations in a single step.


Differences and Usage Notes
---------------------------
- **chat** vs. **communicate**:
  - ``chat`` is more manual: you supply how the conversation 
    is built, and it returns an :class:`AssistantResponse`. 
    It does **not** automatically store those messages unless you do so.  
  - ``communicate`` is simpler: it automatically adds new messages 
    (user + response) to the conversation, optionally validates 
    the LLM output with a pydantic model or partial fields.

- **operate** vs. **instruct**:
  - ``operate`` is an advanced, multi-step approach with an 
    internal “Operative” model. It can parse a structured response 
    and run any requested tool calls.  
  - ``instruct`` is a simpler convenience method that decides 
    between “communicate” or “operate” based on the user's 
    :class:`Instruct` contents.

- **ReAct**:
  - A subset of advanced usage where the model is expected to 
    produce chain-of-thought or partial reasoning steps that 
    may loop if it finds it needs further expansions.

- **_act** vs. **act**:
  - ``_act`` is an internal helper that does the actual invocation 
    of a tool, returning an :class:`ActionResponse`.  
  - ``act`` is the user-facing method for one or multiple 
    function calls, supporting concurrency, error suppression, 
    or basic retry logic.

- **interpret**:
  - Focused on rewriting or “polishing” user text into a more 
    formal/explicit prompt. Doesn't store new messages.

- **parse**:
  - Takes a final text and converts it to a pydantic model or 
    dictionary. Usually used if you need structured data from 
    a raw LLM response but don't want that to be part of the 
    conversation.  

In practice, these operations can be freely combined to build 
complex pipelines—**for example**, you might 
:func:`interpret` the user input, then :func:`operate`, 
then parse final results or call custom logic.

----

File References
---------------
These operations are scattered in files (like `_act.py`, 
`chat.py`, `communicate.py`, etc.), but each is also exposed 
directly as a method on :class:`~lionagi.session.branch.Branch`.

``_act`` -> ``lionagi.operations._act.act._act``  
``chat`` -> ``lionagi.operations.chat.chat``  
``communicate`` -> ``lionagi.operations.communicate.communicate``  
``operate`` -> ``lionagi.operations.operate.operate``  
``parse`` -> ``lionagi.operations.parse.parse``  
``instruct`` -> ``lionagi.operations.instruct.instruct``  
``interpret`` -> ``lionagi.operations.interpret.interpret``  
``ReAct`` -> ``lionagi.operations.ReAct.ReAct``  
``select`` -> ``lionagi.operations.select.select``  
``translate`` -> ``lionagi.operations.translate.translate``

``act`` is simply a method in 
``lionagi.session.branch.Branch.act`` that calls 
``_act`` for each request.

``Branch`` itself is documented separately in 
:ref:`lionagi-branch-class`.

----

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
