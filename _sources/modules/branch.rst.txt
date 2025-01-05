===================================
Branch
===================================
A **Branch** in LionAGI coordinates multiple subsystems—**messages**, 
**tools** (action manager), **models** (iModel manager), and **logs**—into 
a single “conversation or operation” context. It acts as a high-level 
orchestrator for conversation flows, tool invocation, log recording, 
and even inter-branch messaging (via a :class:`Mailbox`).



-----------------------
1. The ``Branch`` Class
-----------------------
.. module:: lionagi.session.branch
   :synopsis: Manages a conversation “branch” with messages, tools, and iModels.

.. class:: Branch

   **Inherits from**: :class:`Element`, :class:`Communicatable`, :class:`Relational`

   A Branch in LionAGI ties together:

   - :class:`MessageManager` (`msgs` property):  
     Manages conversation messages. Provides adding instructions, assistant 
     responses, or other specialized messages.

   - :class:`ActionManager` (`acts` property):  
     Registers and invokes **tools** (functions). E.g. calls 
     :meth:`ActionManager.invoke(...)` for a given function name + arguments.

   - :class:`iModelManager` (`mdls` property):  
     Holds references to a “chat” model and a “parse” model, 
     enabling LLM calls for both conversation and parsing tasks.

   - :class:`LogManager`:  
     For storing logs when the user or system performs an action 
     or receives new data.

   - :attr:`mailbox`:  
     A :class:`Mailbox` for sending/receiving “Mail” objects to other 
     branches or external systems in a multi-agent scenario.

   **Key Methods**:

   - **Conversation**:
     
     - :meth:`communicate(...)`:
       A simpler approach to sending user instructions to the LLM 
       (the chat model) and optionally parsing the result into 
       a Pydantic model.

   - **Action**:
     
     - :meth:`invoke_action(...)`:
       Directly calls the :class:`ActionManager` to run a tool 
       with arguments provided (from an :class:`ActionRequest` 
       object or dict).

   - **Orchestration**:
     
     - :meth:`operate(...)`:
       A more advanced flow that can unify conversation 
       (“chat” with the LLM) **and** tool invocation in one step, 
       guided by an :class:`Operative` or typed request/response 
       definitions.
     
     - :meth:`parse(...)`:
       Attempts to parse or validate the raw LLM response 
       (string) into structured data, using the “parse” model 
       from the iModelManager or fallback logic.

   - **Mail**:
     
     - :meth:`send(...)` / :meth:`receive(...)`:
       Moves data in or out of the mailbox to other branches. 
       E.g. you might “send” a tool or message to another agent 
       (branch), or “receive” an iModel from them.

   **Usage Example**::

      from lionagi.session.branch import Branch

      # 1) Create a Branch
      branch = Branch(
          user="external_user",
          name="ChatBranch"
      )

      # 2) Add some message or system context
      branch.msgs.add_message(
          system="You are a system with advanced knowledge..."
      )

      # 3) Communicate with the LLM
      response = await branch.communicate(
          instruction="Hello, how are you?",
          guidance="Be concise",
      )
      print(response)
      # => raw text from the chat model

      # 4) Tools
      def add(x: int, y: int) -> int:
          return x + y

      branch.acts.register_tool(add)
      # or
      # branch.invoke_action({"function": "add", "arguments": {"x":1,"y":2}})


-------------------------
2. Branch Detailed APIs
-------------------------

.. py:method:: operate(...)
   
   The “big orchestrator” method that can both converse with the model 
   **and** check if any tools were requested. If so, it automatically 
   calls :meth:`invoke_action`.

.. py:method:: communicate(...)
   
   A simpler method for calling the chat model with a new user instruction. 
   If you want no “tool invocation,” this is often enough.

.. py:method:: parse(...)
   
   Helper to re-check or refine an LLM response using 
   the “parse model,” potentially applying fuzzy matching 
   or partial validation.

.. py:method:: invoke_action(...)
   
   A direct call to :class:`ActionManager.invoke(...)`, 
   but integrated into the branch’s logs and message system.


-----------------------------------
3. Multi-branch / Multi-agent Usage
-----------------------------------
If you have multiple :class:`Branch` objects, you can treat them 
like separate “agents” or conversation threads:

1. Each has its own messages, tools, iModels, logs, and a mailbox.
2. You can :meth:`send` a package from one branch’s mailbox 
   to another’s ID. The second branch must :meth:`receive` it 
   to incorporate that new data (which might be a new tool, 
   a new system message, or an updated model).

The mailbox approach fosters a **loose coupling**: branches only 
exchange exactly what you mail.


---------------------
4. Cloning a Branch
---------------------
.. py:method:: clone(sender: ID.Ref=None) -> Branch

Duplicates all messages, logs, and tools into a new instance:

- Typically used if you want to “branch out” the conversation 
  or scenario from a given state, preserving all data so far 
  but continuing in a new direction. 
- The optional ``sender`` argument sets the **sender** ID on 
  all cloned messages.


-----------------------
5. Example Flow
-----------------------
Below is a short pseudo-code showing usage:

.. code-block:: python

   from lionagi.session.branch import Branch

   # 1) Create initial branch
   br = Branch(name="ExampleBranch")

   # 2) Communicate with LLM
   res = await br.communicate(instruction="Summarize recent logs")

   # 3) Suppose we want to parse the response with a custom model
   from pydantic import BaseModel

   class SummModel(BaseModel):
       summary: str

   summary_res = await br.communicate(
       instruction="Now parse the summary properly",
       response_format=SummModel
   )
   # => returns a SummModel instance with a 'summary' field

   # 4) If we define a tool that processes the summary:
   def refine_summary(text: str) -> str:
       return text[:100]  # truncated for example

   br.acts.register_tool(refine_summary)
   # 5) Possibly operate
   final = await br.operate(
       instruction={"task": "Refine the existing summary"},
       actions=True,  # allow or require tool usage
   )


-----------------
Summary
-----------------
**Branch** ties together multiple sub-managers (messages, actions, iModels, logs)
and provides high-level methods (like :meth:`operate`) that handle **both** 
LLM calls and **tool invocation** seamlessly. For advanced multi-agent or 
multi-step scenarios, the Branch class is your main orchestrator, ensuring 
**consistency** and **integration** among the subsystems.
