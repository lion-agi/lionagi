.. _lionagi-mail-system:

======================================
Mail System
======================================
.. module:: lionagi.protocols.mail
   :synopsis: Provides messaging abstractions including Mail, Mailbox, Exchange, and MailManager.

Overview
--------
The **mail system** in LionAGI enables asynchronous exchange of messages (mail)
across multiple sources that implement :class:`Communicatable`. The components
include:

- :class:`Exchange`: Coordinates mail flow among sources in a buffer-based approach.
- :class:`Mail`: The fundamental message unit, containing a :class:`Package`.
- :class:`Mailbox`: Local storage for inbound and outbound mail at a single source.
- :class:`MailManager`: An alternative (often higher-level) manager for mail distribution.
- :class:`Package` / :class:`PackageCategory`: Wraps the content or payload with a categorized type.

Contents
--------
.. contents::
   :local:
   :depth: 2


Exchange
--------
.. class:: Exchange
   :module: lionagi.protocols.mail.exchange

   **Inherits from**: :class:`~lionagi.protocols.generic.element.Element`

   Manages mail exchange operations among a set of sources that are Communicatable. Each source has an associated Mailbox to store inbound and outbound mail.

   The Exchange uses an internal buffer for collecting mail from each sender's mailbox and delivering messages to the correct recipient's mailbox.

    Attributes
    ----------
    sources : Pile[Communicatable]
        The communicatable sources participating in the exchange
    buffer : dict[IDType, list[Mail]]
        A temporary holding area for mail messages before they reach their recipient's mailbox
    mailboxes : dict[IDType, Mailbox]
        Maps each source's ID to its Mailbox
    _execute_stop : bool
        A flag indicating whether to stop the asynchronous execution loop

    Methods
    -------
    add_source(sources)
        Register new communicatable sources for mail exchange

    delete_source(sources)
        Remove specified sources from the exchange, clearing any pending mail

    create_mail(sender, recipient, category, item, request_source=None)
        Helper method to create a new Mail instance

    collect(sender)
        Collect all outbound mail from a specific sender, moving it to the exchange buffer

    deliver(recipient)
        Deliver all mail in the buffer addressed to a specific recipient

    collect_all()
        Collect mail from every source in this exchange

    deliver_all()
        Deliver mail to every source in this exchange

    execute(refresh_time=1)
        Continuously collect and deliver mail in an asynchronous loop

    Parameters
    ----------
    sources : ID[Communicatable].ItemSeq, optional
        One or more communicatable sources to manage. If provided, they are immediately added.

    Notes
    -----
    The Exchange class orchestrates mail flows among sources that implement Communicatable. 
    It collects pending outgoing mail from each source and delivers them to the appropriate 
    recipients using an internal buffer system.


Mail
----
.. class:: Mail(Element, Sendable)
   :module: lionagi.protocols.mail.mail

   A single mail message that can be sent between communicatable entities. It includes a sender, recipient, and a package that describes the mail's content.

    Encapsulates a single unit of mail with a sender, recipient, and a :class:`Package`. As a subclass of :class:`~lionagi.protocols.generic.element.Element`, it is also observable and can be tracked or logged.

    Attributes
    ----------
    sender : IDType
        The ID representing the mail sender
    recipient : IDType
        The ID representing the mail recipient
    package : Package
        The package (category + payload) contained in this mail

    Properties
    ----------
    category : PackageCategory
        Shortcut for retrieving the category from the underlying package

    Methods
    -------
    _validate_sender_recipient(value)
        Validate that the sender and recipient fields are correct IDTypes

    Notes
    -----
    The Mail class is a Sendable element representing a single piece of mail, carrying a Package between a sender and recipient. It provides validation for sender and recipient IDs and easy access to the package's category.


Mailbox
-------
.. class:: Mailbox

    A mailbox that accumulates inbound and outbound mail for a single communicatable source.

    A mailbox stores inbound and outbound mail for a **single** source. Inbound mail is grouped by sender, and outbound mail is queued in a progression for dispatch.

    Attributes
    ----------
    pile_ : Pile[Mail]
        A concurrency-safe collection storing all mail items
    pending_ins : dict[IDType, Progression]
        Maps each sender's ID to a progression of inbound mail
    pending_outs : Progression
        A progression of mail items waiting to be sent (outbound)

    Properties
    ----------
    senders : list[str]
        List of sender IDs that have inbound mail in this mailbox

    Methods
    -------
    append_in(item)
        Add a mail item to the inbound queue for the item's sender

    append_out(item)
        Add a mail item to the outbound (pending_outs) queue

    exclude(item)
        Remove a mail item from all internal references (inbound, outbound, and pile)

    __contains__(item)
        Check if a mail item is currently in this mailbox

    __bool__()
        Indicates if the mailbox contains any mail

    __len__()
        Number of mail items in this mailbox

    Notes
    -----
    The Mailbox class implements a simple mailbox system for each Communicatable entity. 
    It holds inbound and outbound mail, stored internally in a Pile for thread-safe access.


MailManager
-----------
.. class:: MailManager(Manager)

    A manager for mail operations across various observable sources within LionAGI. Unlike Exchange, this class can manage the state of multiple sources in a more general or higher-level context, storing mail queues in a dictionary rather than individual buffers.

    Provides a manager-level approach to mail distribution, storing mail in a dictionary keyed by recipient and sender. It can "collect" from each source and "send" to each recipient, optionally running in an asynchronous loop.

    Attributes
    ----------
    sources : Pile[Observable]
        A concurrency-safe collection of known sources
    mails : dict[str, dict[str, deque]]
        A nested mapping of recipient -> sender -> queue of mail
    execute_stop : bool
        Controls the asynchronous execution loop; set to True to exit

    Methods
    -------
    add_sources(sources)
        Register new sources in the MailManager

    delete_source(source_id)
        Remove a source from the manager, discarding any associated mail

    create_mail(sender, recipient, category, package, request_source=None)
        Factory method to generate a Mail object

    collect(sender)
        Collect outbound mail from a single source

    send(recipient)
        Send any pending mail to a specified recipient

    collect_all()
        Collect outbound mail from all known sources

    send_all()
        Send mail to all known recipients who have pending items

    execute(refresh_time=1)
        Continuously collect and send mail in an asynchronous loop

    Parameters
    ----------
    sources : ID.Item | ID.ItemSeq, optional
        Initial source(s) to manage. Each source must be an Observable.

    Notes
    -----
    The MailManager class coordinates mail operations across multiple sources in a more abstract or high-level manner compared to Exchange. It stores mail queues in a dictionary rather than individual buffers, making it suitable for managing the state of multiple sources in a more general context.


Package and PackageCategory
---------------------------
.. class:: PackageCategory(str, Enum)

    Enumeration of common package categories in LionAGI.

    An enumeration that describes various categories (e.g., "message," "tool," "signal") associated with the :class:`Package`.

    Members
    -------
    MESSAGE : str
        General message content
    TOOL : str
        A tool or action to be invoked
    IMODEL : str
        Some internal model reference
    NODE : str
        A node in a graph
    NODE_LIST : str
        A list of nodes
    NODE_ID : str
        A node ID
    START : str
        A 'start' signal
    END : str
        An 'end' signal
    CONDITION : str
        A condition or gating logic
    SIGNAL : str
        A more generic signal or marker

.. class:: Package(Observable)

    A self-contained package that can be attached to Mail items. Includes a unique ID, creation timestamp, category, payload item, and an optional request source for context.

    Holds the main payload data and classification for each mail. Optionally includes a reference to the request origin.

    Attributes
    ----------
    category : PackageCategory
        The classification or type of package
    item : Any
        The main payload or data of this package
    request_source : ID[Communicatable] | None
        An optional reference indicating the origin or context for this package
    id : IDType
        A unique identifier for this package
    created_at : float
        Timestamp indicating when this package was created

    Parameters
    ----------
    category : PackageCategory
        The classification or type of package
    item : Any
        The main payload or data of this package
    request_source : ID[Communicatable], optional
        An optional reference indicating the origin or context for this package

    Notes
    -----
    The Package class is designed to be a self-contained unit that can be attached to Mail items. 
    It uses slots for memory efficiency and includes validation for the package category.


-----------------
Usage Example
-----------------
Below is a simple usage scenario demonstrating these components:

.. code-block:: python

   from lionagi.protocols.mail.exchange import Exchange
   from lionagi.protocols.mail.mail import Mail
   from lionagi.protocols.mail.mail_manager import MailManager
   from lionagi.protocols.mail.package import PackageCategory
   from lionagi.protocols._concepts import Communicatable

   class MySource(Communicatable):
       # Must define 'mailbox' and 'send' method for Communicatable
       def __init__(self):
           self.id = ...
           self.mailbox = ...
       def send(self, mail):
           self.mailbox.append_out(mail)

   # Create two sources
   srcA, srcB = MySource(), MySource()

   # Approach 1: Use Exchange
   exchange = Exchange([srcA, srcB])
   mail = exchange.create_mail(
       sender=srcA,
       recipient=srcB,
       category=PackageCategory.MESSAGE,
       item="Hello from A!"
   )
   srcA.send(mail)
   exchange.collect_all()
   exchange.deliver_all()

   # Approach 2: Use MailManager
   manager = MailManager([srcA, srcB])
   mail2 = manager.create_mail(
       sender=srcA.id,
       recipient=srcB.id,
       category=PackageCategory.MESSAGE,
       package="Another greeting"
   )
   # Normally you'd place mail2 in srcA's mailbox, then manager.collect_all() -> manager.send_all().


File Locations
--------------
- **Exchange**: ``lionagi/protocols/mail/exchange.py``
- **Mail**: ``lionagi/protocols/mail/mail.py``
- **Mailbox**: ``lionagi/protocols/mail/mailbox.py``
- **MailManager**: ``lionagi/protocols/mail/manager.py``
- **Package** & **PackageCategory**: ``lionagi/protocols/mail/package.py``

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
