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
.. autoclass:: lionagi.protocols.mail.exchange.Exchange
   :members:
   :undoc-members:
   :show-inheritance:

   The Exchange uses an internal buffer for collecting mail from each sender's
   mailbox and delivering messages to the correct recipient's mailbox.


Mail
----
.. autoclass:: lionagi.protocols.mail.mail.Mail
   :no-index:
   :members:
   :undoc-members:
   :show-inheritance:

   Encapsulates a single unit of mail with a sender, recipient, and a :class:`Package`.
   As a subclass of :class:`~lionagi.protocols.generic.element.Element`, it is
   also observable and can be tracked or logged.


Mailbox
-------
.. autoclass:: lionagi.protocols.mail.mailbox.Mailbox
   :members:
   :undoc-members:
   :show-inheritance:

   A mailbox stores inbound and outbound mail for a **single** source. Inbound mail
   is grouped by sender, and outbound mail is queued in a progression for dispatch.


MailManager
-----------
.. autoclass:: lionagi.protocols.mail.manager.MailManager
   :members:
   :undoc-members:
   :show-inheritance:

   Provides a manager-level approach to mail distribution, storing mail in a
   dictionary keyed by recipient and sender. It can “collect” from each source
   and “send” to each recipient, optionally running in an asynchronous loop.


Package and PackageCategory
---------------------------
.. autoclass:: lionagi.protocols.mail.package.PackageCategory
   :members:
   :undoc-members:

   An enumeration that describes various categories (e.g., “message,” “tool,”
   “signal”) associated with the :class:`Package`.

.. autoclass:: lionagi.protocols.mail.package.Package
   :no-index:
   :members:
   :undoc-members:
   :show-inheritance:

   Holds the main payload data and classification for each mail. Optionally
   includes a reference to the request origin.


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
