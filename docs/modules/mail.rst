==============================
Mail
==============================

The LionAGI **mail system** provides a framework for sending and receiving
messages (or “mail”) among **communicatable** entities. This is useful for
agent-to-agent communication, scheduling tasks, and distributing work packages
in a multi-agent or distributed LionAGI environment.

Key Concepts
============

- **Mail**: Represents an atomic message or package, carrying a
  :class:`Package` with some data. It includes sender and recipient
  IDs (both referencing **Communicatable** objects).
- **Mailbox**: A container holding incoming and outgoing ``Mail`` items
  for a given communicatable entity.
- **Exchange**: Manages a set of communicatable sources, collecting mail
  from each source’s outbox and delivering it to the intended recipient’s
  inbox, optionally in an asynchronous loop.
- **MailManager**: An alternative manager for mail distribution,
  collecting and sending mail from a set of sources in a loop
  (somewhat parallel to ``Exchange``). 
- **Package**: The payload carried by a ``Mail``. Has a category
  (e.g., ``MESSAGE``, ``TOOL``, etc.) and an item (data).
- **PackageCategory**: An enum listing possible categories (like
  ``MESSAGE``, ``TOOL``, ``IMODEL``, etc.).

All classes leverage LionAGI’s base concepts (e.g., :class:`Element`
for unique IDs and timestamps, :class:`Communicatable` for objects
that can send/receive mail).



---------------------------
1. The ``Mail`` Class
---------------------------
.. module:: lionagi.protocols.mail.mail
   :synopsis: Core representation of a single mail piece.

.. class:: Mail
   :extends: lionagi.protocols.generic.element.Element
   :implements: lionagi.protocols._concepts.Sendable

A single piece of mail, referencing a :attr:`sender`, a :attr:`recipient`,
and carrying a :attr:`package`.

**Key Attributes**:

- :attr:`sender`: The :class:`IDType` of the entity sending this mail
  (must be a **Communicatable**).
- :attr:`recipient`: The :class:`IDType` of the entity receiving this mail
  (also a **Communicatable**).
- :attr:`package`: A :class:`Package` instance holding the actual data.

**Properties**:

- :attr:`category`: Shortcut to ``mail.package.category`` (the
  :class:`PackageCategory` of the payload).

**Example**::

   from lionagi.protocols.mail.mail import Mail
   from lionagi.protocols.mail.package import Package, PackageCategory
   from lionagi.protocols.generic.element import IDType

   mail = Mail(
       sender=IDType.create(),
       recipient=IDType.create(),
       package=Package(category=PackageCategory.MESSAGE, item="Hello!")
   )
   print(mail.category)    # => PackageCategory.MESSAGE


------------------------------
2. The ``Package`` + Category
------------------------------
.. module:: lionagi.protocols.mail.package
   :synopsis: Defines the payload of a mail item.

.. class:: Package
   :extends: lionagi.protocols.generic.element.Element

Wraps the actual payload in :attr:`item` along with a :attr:`category`
(for instance, ``MESSAGE``, ``TOOL``, ``NODE_ID``, etc.) and an optional
:attr:`request_source` indicating who requested this package.

**Fields**:

- :attr:`category`: A :class:`PackageCategory` enumerating the type of content.
- :attr:`item`: Arbitrary data carried by the package.
- :attr:`request_source`: If relevant, identifies the original communicator 
  that requested the item.

**Example**::

   from lionagi.protocols.mail.package import Package, PackageCategory

   p = Package(
       category=PackageCategory.MESSAGE,
       item="Any content goes here"
   )
   print(p.item)         # => "Any content goes here"
   print(p.category)     # => PackageCategory.MESSAGE


.. class:: PackageCategory
   :module: lionagi.protocols.mail.package

An ``Enum`` listing possible categories for a :class:`Package`. Examples:
``MESSAGE``, ``TOOL``, ``IMODEL``, ``NODE_ID``, ``SIGNAL``, etc.

**Example**::

   from lionagi.protocols.mail.package import PackageCategory

   cat = PackageCategory.MESSAGE
   print(cat.value)  # => "message"


--------------------
3. ``Mailbox``
--------------------
.. module:: lionagi.protocols.mail.mailbox
   :synopsis: Holds incoming/outgoing mail for a single communicator.

.. class:: Mailbox

Each **Communicatable** entity typically has a ``Mailbox`` to store mail. 
There are separate structures for **incoming** (``append_in``) and 
**outgoing** (``append_out``) mail, plus a shared :class:`~lionagi.protocols.generic.pile.Pile` 
where everything is kept.

**Attributes**:

- :attr:`pile_`:
  A :class:`~lionagi.protocols.generic.pile.Pile` containing all mail known
  to the mailbox (incoming + outgoing).
- :attr:`pending_ins`:
  A dictionary mapping **sender** ID to a :class:`~lionagi.protocols.generic.progression.Progression`
  of mail items from that sender.
- :attr:`pending_outs`:
  A :class:`~lionagi.protocols.generic.progression.Progression` listing 
  mail items to be sent out from this mailbox.

**Key Methods**:

- :meth:`append_in(item)`: Mark a mail item as incoming (from some sender).
- :meth:`append_out(item)`: Mark a mail item as outgoing (ready to be 
  collected and delivered).
- :meth:`exclude(item)`: Remove a mail from the mailbox entirely.

**Example**::

   from lionagi.protocols.mail.mailbox import Mailbox
   from lionagi.protocols.mail.mail import Mail

   box = Mailbox()
   # Suppose we have a mail object 'm'
   box.append_in(m)   # now 'm' is in incoming
   # or
   box.append_out(m)  # now 'm' is pending to be sent out


--------------------
4. ``Exchange``
--------------------
.. module:: lionagi.protocols.mail.exchange
   :synopsis: Collects and delivers mail among a set of communicatable sources.

.. class:: Exchange

Manages a set of **Communicatable** sources, each having a mailbox. 
**Collect** mail from each source’s ``pending_outs``, buffer it, then 
**deliver** it to the intended recipient’s mailbox (``append_in``). 
An optional asynchronous :meth:`execute` loop can repeatedly gather 
and send all mail.

**Attributes**:

- :attr:`sources`: A :class:`~lionagi.protocols.generic.pile.Pile` of 
  :class:`Communicatable` objects.
- :attr:`buffer`: A dict that temporarily stores mail for each recipient 
  until it’s delivered.
- :attr:`mailboxes`: A dict mapping each communicator’s ID to its :class:`Mailbox`.

**Key Methods**:

- :meth:`add_source(sources)`: Registers new communicator(s).
- :meth:`collect(sender)`: Collect mail from the sender’s outbox into the buffer.
- :meth:`deliver(recipient)`: Deliver buffered mail to a recipient’s inbox.
- :meth:`collect_all()` / :meth:`deliver_all()`: Collect from all, deliver to all.
- :meth:`execute(refresh_time=1)`: Runs a loop that repeatedly calls 
  collect_all/deliver_all.

**Example**::

   from lionagi.protocols.mail.exchange import Exchange
   from lionagi.protocols.mail.mail import Mail
   from lionagi.protocols.mail.package import Package, PackageCategory
   # Suppose we have a few Communicatable entities, each with a mailbox.

   exch = Exchange([comm1, comm2, comm3])
   # Create a mail item from comm1 to comm2
   mail = exch.create_mail(
       sender=comm1.id, 
       recipient=comm2.id,
       category=PackageCategory.MESSAGE,
       item="Hello from comm1!"
   )
   # Place mail in comm1's outbox
   comm1.mailbox.append_out(mail)

   # Collect from comm1 -> exch.buffer
   exch.collect(sender=comm1.id)
   # Deliver to comm2's mailbox
   exch.deliver(recipient=comm2.id)


------------------------
5. ``MailManager``
------------------------
.. module:: lionagi.protocols.mail.mail_manager
   :synopsis: Alternative mail distribution approach.

.. class:: MailManager
   :extends: lionagi.protocols._concepts.Manager

Another manager for mail flow among multiple sources. It holds a 
:class:`~lionagi.protocols.generic.pile.Pile` of sources (like 
:class:`Exchange` does), offering `collect`/`send` methods to route mail. 
It can also run an async :meth:`execute` method in a loop.

**Attributes**:

- :attr:`sources`: Pile of observable entities (each presumably communicatable).
- :attr:`mails`: A dictionary that temporarily caches mail for each recipient.

**Key Methods**:

- :meth:`add_sources(...)`: Add new sources.
- :meth:`create_mail(...)`: Create a new :class:`Mail`.
- :meth:`delete_source(...)`: Remove a source from management.
- :meth:`collect(sender)`: Gather mail from a sender’s outbox.
- :meth:`send(recipient)`: Send all mail queued up for the given recipient.
- :meth:`collect_all()`, :meth:`send_all()`
- :meth:`execute(...)`: Run the collection/sending cycle asynchronously in a loop.

**Example**::

   from lionagi.protocols.mail.mail_manager import MailManager

   mm = MailManager([comm1, comm2, comm3])
   # Create a mail object
   mail = mm.create_mail(
       sender=comm1.id,
       recipient=comm2.id,
       category="message",
       package="Hello from comm1!"
   )
   # Put mail into comm1's outbox
   comm1.mailbox.append_out(mail)

   # Now, do a cycle of collecting and sending
   mm.collect_all()
   mm.send_all()
   # comm2 should now have the mail in its mailbox


-----------------
Usage Scenarios
-----------------
1. **Agent Communication**  
   Each agent (Communicatable) can place mail into its outbox, which is then
   collected by an :class:`Exchange` or :class:`MailManager` and delivered
   to the correct recipient. This decouples agents from direct function calls.

2. **Distributing Work**  
   In a multi-component system, tasks or job requests can be wrapped as
   :class:`Package` objects. Each agent sees only the mail relevant to it.

3. **Asynchronous Execution**  
   Both :class:`Exchange` and :class:`MailManager` offer an :meth:`execute`
   method that loops with a `refresh_time`, repeatedly calling “collect all”
   and “deliver all.” This suits situations where mail must be polled or
   delivered in real-time intervals.


----------------
Summary
----------------
The mail system in LionAGI provides a flexible approach for **intra- or
inter-agent communication**, built upon:

- **Mail** (individual messages with payloads).
- **Mailbox** (per-agent storage for outbox/inbox).
- **Exchange** or **MailManager** (managers for collecting and distributing mail).

By associating each agent (Communicatable) with a mailbox, you can easily
**decouple** communication, track usage or logs, and integrate with concurrency
mechanisms such as `asyncio`. This promotes **modular** design for complex
LionAGI scenarios where multiple components or agents must exchange tasks and
data in a controlled manner. 
