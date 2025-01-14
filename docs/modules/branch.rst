.. _lionagi-branch-class:

================================================
Branch: The Orchestrator
================================================
.. module:: lionagi.session.branch
   :synopsis: Provides the Branch class to manage conversation, actions, logs, etc.

Overview
--------
A :class:`Branch` represents a single “branch” of conversation in LionAGI.
It **manages**:

- A :class:`~lionagi.protocols.generic.log.LogManager` for storing logs,
- A :class:`~lionagi.protocols.generic.log.LogManagerConfig` (if needed),
- A :class:`~lionagi.protocols.generic.element.Element` as the base object,
- A :class:`~lionagi.protocols.types.Communicatable` mailbox for cross-branch communication,
- A :class:`~lionagi.protocols.types.Relational` link,
- A :class:`~lionagi.protocols.types.SenderRecipient` to identify user or role,
- A :class:`MessageManager` for messages (system instructions, user instructions, model responses),
- An :class:`ActionManager` for tools,
- An :class:`iModelManager` for multiple LLM or model references (like “chat”, “parse”),
- Utility methods for “chat,” “operate,” “parse,” “act,” etc. (documented in :ref:`lionagi-branch-operations`).

Contents
--------
.. contents::
   :local:
   :depth: 2


Branch
------

.. class:: Branch
   :module: lionagi.session.branch

   **Inherits from**: :class:`~lionagi.protocols.generic.element.Element`, :class:`~lionagi.protocols.types.Communicatable`, :class:`~lionagi.protocols.types.Relational`

   Manages a conversation 'branch' with messages, tools, and iModels.

    The Branch class serves as a high-level interface or orchestrator that:
    
    - Handles message management (MessageManager)
    - Registers and invokes tools/actions (ActionManager)
    - Manages model instances (iModelManager)
    - Logs activity (LogManager)
    - Communicates via mailboxes (Mailbox)

    Key responsibilities:
    
    - Storing and organizing messages, including system instructions, user instructions, and model responses
    - Handling asynchronous or synchronous execution of LLM calls and tool invocations
    - Providing a consistent interface for "operate," "chat," "communicate," "parse," etc.

    Parameters
    ----------
    user : SenderRecipient, optional
        The user or sender context for this branch
    name : str, optional
        A human-readable name for this branch
    messages : Pile[RoledMessage], optional
        Initial messages for seeding the MessageManager
    system : System | JsonValue, optional
        Optional system-level configuration or message for the LLM
    system_sender : SenderRecipient, optional
        Sender to attribute to the system message if it is added
    chat_model : iModel | dict, optional
        The primary "chat" iModel for conversation
    parse_model : iModel | dict, optional
        The "parse" iModel for structured data parsing
    imodel : iModel, optional
        Deprecated. Alias for chat_model
    tools : FuncTool | list[FuncTool], optional
        Tools or a list of tools for the ActionManager
    log_config : LogManagerConfig | dict, optional
        Configuration dict or object for the LogManager
    system_datetime : bool | str, optional
        Whether to include timestamps in system messages
    system_template : Template | str, optional
        Optional Jinja2 template for system messages
    system_template_context : dict, optional
        Context for rendering the system template
    logs : Pile[Log], optional
        Existing logs to seed the LogManager
    **kwargs
        Additional parameters passed to Element parent init

    Attributes
    ----------
    user : SenderRecipient | None
        The user or "owner" of this branch (often tied to a session)
    name : str | None
        A human-readable name for this branch
    mailbox : Mailbox
        A mailbox for sending and receiving Package objects to/from other branches
    system : System | None
        The system message/configuration, if any
    msgs : MessageManager
        Returns the associated MessageManager
    acts : ActionManager
        Returns the associated ActionManager for tool management
    mdls : iModelManager
        Returns the associated iModelManager
    messages : Pile[RoledMessage]
        Convenience property to retrieve all messages from MessageManager
    logs : Pile[Log]
        Convenience property to retrieve all logs from the LogManager
    chat_model : iModel
        The primary "chat" model (iModel) used for conversational LLM calls
    parse_model : iModel
        The "parse" model (iModel) used for structured data parsing
    tools : dict[str, Tool]
        All registered tools (actions) in the ActionManager

    Notes
    -----
    Common usage:
    1. Instantiate a Branch, optionally providing a system message and some initial tools
    2. Use chat() or communicate() for user queries
    3. If you want structured responses or function calls, use operate()
    4. If you want to parse or validate final text, use parse()
    5. Tools can be registered anytime via acts or with the arguments to the constructor

    Also includes mailbox-based methods like send() and receive() for cross-branch 
    or cross-system communication in a multi-agent scenario.


Key Differences from a Basic Session
------------------------------------
Where a simpler “session” might just store messages + call an LLM, 
**Branch** expands that concept by:

- Integrating advanced log management with a :class:`LogManager`.
- Holding a mailbox (like an email or queue system) so that branches 
  can pass :class:`Package` objects to each other.
- Tying in a :class:`ActionManager` for immediate function or tool calls.
- Potentially linking to a “Graph” node or referencing relations 
  (due to the :class:`Relational` inheritance).
- Providing **clone** operations if you want to copy the conversation 
  state to a new branch.

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
