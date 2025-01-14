====================================
Session
====================================

A **Session** in LionAGI manages multiple conversation “branches” and the 
mail transfer mechanism between them. It provides a higher-level container 
for coordinating multiple parallel or sequential Branches, handling 
multi-agent or multi-threaded conversation flows. Each branch has its own 
messages, tools, iModels, and logs, while the Session orchestrates how 
they interact.



---------------------
1. The ``Session`` Class
---------------------
.. module:: lionagi.session.session
   :synopsis: Manages multiple conversation branches and mail exchange.

.. class:: Session
   :extends: Node, Communicatable, Relational

**Purpose**:
- Holds a collection of :class:`Branch` objects in :attr:`branches`.
- Maintains a :attr:`default_branch` for convenience (the main or 
  currently active branch).
- Optionally organizes **mail exchange** via :class:`MailManager` 
  or :class:`Exchange` for multi-agent or multi-branch communication.

**Key Attributes**:

- :attr:`branches` (:class:`Pile[Branch]`):
  The collection of branches in this session.

- :attr:`default_branch` (:class:`Branch`):
  One branch designated as the “default” conversation context. 
  If none is specifically set, it's the first created.

- :attr:`mail_transfer` (:class:`Exchange`):
  Manages sending/receiving mail for these branches (not always 
  strictly needed, but helpful in multi-agent use-cases).

- :attr:`mail_manager` (:class:`MailManager`):
  Alternative mail manager approach, also controlling which 
  sources are recognized as senders/recipients.


-------------------
2. Creation & Basics
-------------------
When you create a **Session**, it automatically initializes:

1. An empty :class:`Pile[Branch]`.
2. A “default branch” (though you can override it).
3. A :class:`MailManager` plus a potential :class:`Exchange`.

**Example**::

   from lionagi.session.session import Session

   sess = Session()
   # -> a new session with a default Branch

   # create an additional branch
   br2 = sess.new_branch(name="SecondConversation")


--------------------------
3. Branch Management
--------------------------
**Branch Lifecycle**:

- :meth:`new_branch(...)`:
  Creates a new :class:`Branch`, optionally specifying system message, 
  user ID, initial tools, etc. The new branch is included in the 
  session's :attr:`branches`, and if there was no default branch, 
  it sets this new one as default.

- :meth:`remove_branch(branch, delete=False)`:
  Removes a branch from the session (by ID or object). If 
  ``delete=True``, it also tries to delete the branch object 
  in memory (though in Python, it just drops references).

- :meth:`split(branch)` / :meth:`asplit(branch)`:
  Clones an existing branch, preserving its messages and tools, 
  creating a new one in the session. This is helpful if you want 
  to “fork” the conversation.

- :meth:`change_default_branch(branch)`:
  Points :attr:`default_branch` to another existing branch.


---------------------
4. Mail Operations
---------------------
**Session** includes:

- :attr:`mail_transfer` (Exchange)
- :attr:`mail_manager` (MailManager)

A session might manage multi-branch mail flows:

- :meth:`collect(...)`: Collect mail from specific branches (or all).
- :meth:`send(...)`: Send mail to specific branches (or all).
- :meth:`collect_send_all(receive_all=False)`:
  Combined approach to gather all outgoing mail from branches, send 
  to recipients, and optionally have them “receive” it as well, 
  so messages or tools are recognized in other branches.

**Example**::

   # 1) Suppose we have branch A and B in the session
   # 2) We do something that prepares mail in branch A's outbox
   # 3) We "collect" from A and "send" to B

   sess.collect(from_=[branchA.id])
   sess.send(to_=[branchB.id])
   # branchB can then .receive(...) or we can do
   sess.collect_send_all(receive_all=True)

This centralization ensures you can run multi-agent or multi-branch 
scenarios all within the same Session context.


--------------------------
5. Inspecting Messages
--------------------------
**Concatenation** of messages from multiple branches:

- :meth:`concat_messages(branches=..., exclude_clone=..., exclude_load=...)`
  returns a :class:`Pile[RoledMessage]` with the combined 
  messages from the chosen branches, optionally excluding 
  those flagged as clones or loads.

- :meth:`to_df(...)`:
  Returns a Pandas DataFrame of the combined messages 
  for easy offline analysis or logging.

**Example**::

   # all messages in a DataFrame
   df = sess.to_df(exclude_clone=True)
   print(df.head())


----------------
6. Example Flow
----------------
.. code-block:: python

   from lionagi.session.session import Session

   # 1) Create a Session
   sess = Session()
   # => includes one default branch

   # 2) Possibly create more branches
   new_br = sess.new_branch(name="ResearchThread")
   # => add a second conversation branch

   # 3) Interact in default branch
   final_resp = await sess.default_branch.communicate(
       instruction="Hello, how can I help?",
       guidance="Be concise",
   )

   # 4) Switch default if needed
   sess.change_default_branch(new_br)

   # 5) Tools or multi-branch mail...
   #  Collect from one branch, send to another
   #  or forcibly 'split' a branch to fork the conversation.

   # 6) Inspect messages across all branches
   df = sess.to_df()
   print(df)


------------------
Summary
------------------
**Session** is the top-level aggregator for multi-branch usage within 
LionAGI, uniting:

- A **list of branches** (each with its own conversation context),
- A **mail manager** or **exchange** for multi-agent or multi-thread 
  communication,
- Tools for quickly copying or merging messages between branches 
  (splitting, removing, or changing the default branch).

Hence, the Session offers a robust environment for advanced 
**multi-conversation** or **multi-agent** setups, ensuring 
**coordination** and **integration** at scale.
