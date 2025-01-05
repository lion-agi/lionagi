==========================
Event Architecture
==========================

The **Event system** in LionAGI provides a uniform way to **track, log, and
process** actions or requests. Events typically carry execution details,
status, timings, and potential errors. Two primary examples are:

- :class:`FunctionCalling` — for **local Python function** invocation 
  with optional pre/post-processing.
- :class:`APICalling` — for **external HTTP/AI service** invocation,
  potentially with token usage, streaming, and caching.

All event classes extend a common :class:`Event` base, storing an 
:attr:`execution` object (representing duration, status, response, and errors).



------------------------
The ``Event`` Base Class
------------------------
.. module:: lionagi.protocols.types
   :synopsis: Base definitions for events and execution states.

In LionAGI, an event is typically a subclass of :class:`Event`, which itself 
inherits from :class:`~lionagi.protocols.generic.element.Element`. The 
:class:`Event` base class provides:

- An :attr:`execution` field holding :class:`Execution` metadata 
  (status, duration, response, error).
- A standard :meth:`invoke()` method that child classes can override, 
  capturing start/end times, updating :attr:`execution.status`, and 
  storing errors or results.

For instance, both :class:`FunctionCalling` and :class:`APICalling` 
subclass :class:`Event` and implement their **own** asynchronous 
:meth:`invoke()` logic, plus domain-specific attributes (e.g., arguments 
for function calls, or headers/payloads for API calls).
