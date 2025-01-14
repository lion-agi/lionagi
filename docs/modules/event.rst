.. _lionagi_protocols_generic_event:

==================================================
Event, EventStatus, and Execution
==================================================
.. module:: lionagi.protocols.generic.event
   :synopsis: Defines an Event object with a tracked execution state.

Overview
--------
This module provides a specialized :class:`Event` class, which extends the 
:class:`~lionagi.protocols.generic.element.Element` base with a structured 
:class:`Execution` state. It also introduces :class:`EventStatus`, an 
enumeration that clarifies the state (pending, processing, completed, or 
failed) of an ongoing or finished event.


EventStatus
-----------
.. class:: EventStatus(str, Enum)
   :module: lionagi.protocols.generic.event

   Represents the **lifecycle states** for an action or task execution. 
   Each event can transition from PENDING to PROCESSING, and finally 
   to either COMPLETED or FAILED.

   Members
   -------
   - **PENDING** : str  
     Initial state before execution starts.
   - **PROCESSING** : str  
     Indicates that the event is currently in progress.
   - **COMPLETED** : str  
     The event action completed successfully.
   - **FAILED** : str  
     The event action encountered an error or otherwise failed.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.generic.event import EventStatus

       print(EventStatus.PENDING)  # "pending"
       print(EventStatus.COMPLETED.value)  # "completed"


Execution
---------
.. class:: Execution
   :module: lionagi.protocols.generic.event

   Tracks the **runtime details** of an event, including status, duration, 
   response, and any error messages. Designed to store partial or final results 
   and the overall outcome of an event's execution.

   Attributes
   ----------
   status : EventStatus
       The current status of the event's execution.
   duration : float | None
       Time in seconds that the event took to execute (if known).
   response : Any
       The result or output of the execution. Could be data or a message.
   error : str | None
       Holds an error message if the execution failed.

   Methods
   -------
   .. method:: __init__(duration: float | None = None, response: Any = None, status: EventStatus = EventStatus.PENDING, error: str | None = None)

       Initializes an ``Execution`` instance with optional duration, response,
       status (defaults to :attr:`EventStatus.PENDING`), and error message.

       Parameters
       ----------
       duration : float | None
           Number of seconds the execution took. If unknown, leave as None.
       response : Any
           The result or output of the execution, if any.
       status : EventStatus
           Current status of the execution. Defaults to PENDING.
       error : str | None
           Optional error message if the execution has failed.

   .. method:: __str__() -> str

       Returns a string representation of the execution, indicating the current 
       ``status``, ``duration``, ``response``, and ``error`` fields.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.generic.event import Execution, EventStatus

       exe = Execution(
           duration=3.5,
           response={"result": 42},
           status=EventStatus.COMPLETED,
           error=None
       )
       print(exe)  # e.g. "Execution(status=completed, duration=3.5, response={'result': 42}, error=None)"


Event
-----
.. class:: Event(Element)
   :module: lionagi.protocols.generic.event
   :show-inheritance:

   **Inherits from**: :class:`~lionagi.protocols.generic.element.Element`

   A specialized Element with an :attr:`execution` field to track the status, 
   duration, and result of an operation. This class is designed for scenarios 
   where an action or task is performed and we need to store the outcome or 
   progression data.

   Attributes
   ----------
   execution : Execution
       Stores the execution state of this event. Defaults to a new 
       :class:`Execution` instance (PENDING status, no error).

   Properties
   ----------
   .. attribute:: response

      Gets or sets the :attr:`Execution.response` for this event.

   .. attribute:: status

      Gets or sets the :attr:`Execution.status` for this event.

   .. attribute:: request

      By default returns an empty dictionary. Subclasses may override to 
      provide request payload data relevant to the event.

   Methods
   -------
   .. method:: invoke() -> None
      :async:

      An **asynchronous** method intended to perform the event's main action. 
      Raises :exc:`NotImplementedError` unless overridden by a subclass.

   .. classmethod:: from_dict(data: dict) -> Event

      Always raises :exc:`NotImplementedError`. Events cannot be fully 
      recreated once they have progressed. Override if a specialized 
      behavior is needed.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.generic.event import Event, EventStatus

       class MyEvent(Event):
           async def invoke(self):
               # Custom logic to handle the event
               self.status = EventStatus.PROCESSING
               # do some work...
               self.status = EventStatus.COMPLETED

File Location
-------------
**Source File**: 
``lionagi/protocols/generic/event.py``

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
