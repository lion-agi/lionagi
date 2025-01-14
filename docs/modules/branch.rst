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
.. autoclass:: lionagi.session.branch.Branch
   :members:
   :undoc-members:
   :show-inheritance:

   The key attributes include:
   
   - **Messages** (via :attr:`msgs`)  
   - **Logs** (via :attr:`logs`)  
   - **Tools** (via :attr:`acts`)  
   - **Models** (via :attr:`mdls`)  
   - **Mailbox** (for external messaging)

   **Common usage**:
   1. Instantiate a Branch, optionally providing a system message and some initial tools.
   2. Use :meth:`chat` or :meth:`communicate` for user queries.
   3. If you want structured responses or function calls, use :meth:`operate`.
   4. If you want to parse or validate final text, use :meth:`parse`.
   5. Tools can be registered anytime via :attr:`acts` or with the arguments 
      to the constructor.

   Also includes mailbox-based methods like :meth:`send` and :meth:`receive` 
   for cross-branch or cross-system communication in a multi-agent scenario.


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
