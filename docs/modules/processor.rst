.. _lionagi_protocols_generic_processor:

================================================
Event Processor and Executor
================================================
.. module:: lionagi.protocols.generic.processor
   :synopsis: Defines asynchronous event processing with capacity-limited queues 
              and an Executor for managing events and linking them to a Processor.

Overview
--------
This module provides:

- :class:`Processor`: An **asynchronous** queue manager for :class:`~lionagi.protocols.generic.event.Event` objects, 
  supporting capacity-limited batching and optional permission checks.
- :class:`Executor`: A coordinating class that **stores events** in a :class:`~lionagi.protocols.generic.pile.Pile` 
  and **forwards** them to an internal Processor for execution.


Processor
---------
.. class:: Processor(Observer)
   :module: lionagi.protocols.generic.processor

   **Inherits from**: :class:`~lionagi.protocols._concepts.Observer`

   Manages a queue of events that can be processed asynchronously in **batches**, respecting a 
   capacity limit. Subclasses can override methods for **request_permission** checks or 
   custom handling logic. The processor can be started and stopped, and it refreshes 
   available capacity after each batch of events.

   Attributes
   ----------
   event_type : ClassVar[type[Event]]
       Declares the type of Event this processor is meant to handle. Subclasses 
       should set this to a specific Event subclass if needed.

   queue_capacity : int
       Maximum number of events that can be processed in one batch (e.g., 10).
   capacity_refresh_time : float
       Number of seconds after which the queue capacity is reset (e.g., 5.0).

   queue : asyncio.Queue
       Internal async queue holding incoming events.
   _available_capacity : int
       Tracks the current capacity (resets to :attr:`queue_capacity` after processing).
   _execution_mode : bool
       Indicates if the processor is currently in a continuous `execute` loop.
   _stop_event : asyncio.Event
       An event used to signal a requested stop in the loop.

   Initialization
   --------------
   .. method:: __init__(queue_capacity: int, capacity_refresh_time: float) -> None

      Args
      ----
      queue_capacity : int
          The maximum number of events allowed in a single processing batch.
      capacity_refresh_time : float
          After this many seconds, the capacity is refreshed.

      Raises
      ------
      ValueError
          If ``queue_capacity < 1`` or ``capacity_refresh_time <= 0``.

   Properties
   ----------
   .. attribute:: available_capacity

      Tracks how many more events can be processed in the current batch.

   .. attribute:: execution_mode

      A boolean indicating if the processor's :meth:`execute` method is actively running.

   Methods
   -------
   .. method:: enqueue(event: Event) -> None
      :async:

      Adds an Event to the internal async queue.

   .. method:: dequeue() -> Event
      :async:

      Retrieves the next Event from the queue.

   .. method:: join() -> None
      :async:

      Blocks until the queue is fully processed.

   .. method:: stop() -> None
      :async:

      Signals this processor to stop (sets the internal stop event).

   .. method:: start() -> None
      :async:

      Clears the stop signal, allowing the processor to continue.

   .. method:: is_stopped() -> bool

      Checks whether the processor is in a stopped state.

   .. classmethod:: create(**kwargs: Any) -> Processor
      :async:

      Creates a new instance of ``Processor``, forwarding any kwargs to the constructor.

   .. method:: process() -> None
      :async:

      Retrieves and processes events from the queue, up to :attr:`available_capacity`. 
      Each event's ``status`` is set to :attr:`~lionagi.protocols.generic.event.EventStatus.PROCESSING`
      if it passes a permission check (:meth:`request_permission`). After processing 
      these events, the capacity is reset if any were processed.

   .. method:: request_permission(**kwargs: Any) -> bool
      :async:

      Determines whether an event is allowed to proceed. Subclasses can override
      to implement rate limiting, user permissions, or other custom checks.

   .. method:: execute() -> None
      :async:

      Continuously processes events until :meth:`stop` is called, sleeping 
      for :attr:`capacity_refresh_time` between cycles to refresh capacity.


Executor
--------
.. class:: Executor(Observer)
   :module: lionagi.protocols.generic.processor

   **Inherits from**: :class:`~lionagi.protocols._concepts.Observer`

   A higher-level manager that **maintains a pile of events** and forwards them 
   to an internal :class:`Processor` for asynchronous execution. This allows 
   classes to store events locally, possibly filter or arrange them, and then 
   dispatch them in batches.

   Attributes
   ----------
   processor_type : ClassVar[type[Processor]]
       Declares which Processor subclass to use for event handling.
   processor_config : dict[str, Any]
       A dictionary of initialization arguments for :attr:`processor`.
   pending : Progression
       Tracks IDs of events that are ready to be forwarded to the processor.
   processor : Processor | None
       The internal processor instance; created lazily if None.
   pile : Pile[Event]
       A pile storing all events, enabling concurrency-safe access and 
       type constraints.

   Initialization
   --------------
   .. method:: __init__(processor_config: dict[str, Any] | None = None, strict_event_type: bool = False) -> None

      Args
      ----
      processor_config : dict[str, Any] | None
          Configuration parameters for creating the processor (e.g., capacity, refresh time).
      strict_event_type : bool
          If True, the underlying :class:`Pile` enforces exact type matching for 
          :class:`~lionagi.protocols.generic.event.Event` objects.

   Properties
   ----------
   .. attribute:: event_type

      The type of event the processor handles (mirrors :attr:`processor_type.event_type`).

   .. attribute:: strict_event_type

      Whether the Pile requires exact type checks for added events.

   Methods
   -------
   .. method:: forward() -> None
      :async:

      Sends all pending events from the :attr:`pile` to the :attr:`processor`, 
      then calls :meth:`processor.process` immediately.

   .. method:: start() -> None
      :async:

      If the processor does not exist, create it with :meth:`_create_processor`. Then
      calls :meth:`processor.start` to enable event processing.

   .. method:: stop() -> None
      :async:

      Stops the processor if it is active.

   .. method:: append(event: Event) -> None
      :async:

      Adds a new :class:`~lionagi.protocols.generic.event.Event` to the pile and 
      queues its ID in :attr:`pending`. 

   .. property:: completed_events -> Pile[Event]
      Returns a new pile containing all events marked :attr:`~lionagi.protocols.generic.event.EventStatus.COMPLETED`.

   .. property:: pending_events -> Pile[Event]
      Returns a new pile containing all events still at :attr:`~lionagi.protocols.generic.event.EventStatus.PENDING`.

   .. property:: failed_events -> Pile[Event]
      Returns a new pile containing all events at :attr:`~lionagi.protocols.generic.event.EventStatus.FAILED`.

   .. method:: __contains__(ref: ID[Event].Ref) -> bool

      Checks if a given event or event ID reference is stored in :attr:`pile`.

   Private Methods
   ----------------
   .. method:: _create_processor() -> None
      :async:

      Private instance method that instantiates the :attr:`processor` using the stored :attr:`processor_config`.

File Location
-------------
**Source File**: 
``lionagi/protocols/generic/processor.py``

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
