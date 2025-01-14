==================================
API Service System
==================================

The **Service** subsystem in LionAGI provides classes and utilities
for **API endpoint** management (e.g., chat completions), **rate-limiting**,
and orchestrating requests to external language model services. This
system helps unify how LionAGI communicates with various model providers
(OpenAI, Anthropic, Groq, etc.) while handling token usage, endpoint
configuration, caching, and concurrency constraints.


--------------------------
1. EndpointConfig & EndPoint
--------------------------
.. module:: lionagi.service.endpoints.base
   :synopsis: Defines the base classes for endpoint configuration and invocation.

.. class:: EndpointConfig

   **Inherits from**: :class:`pydantic.BaseModel`

Describes the essential attributes of an API endpoint:

- :attr:`provider` (str|None): The backend provider name (e.g., "openai").
- :attr:`base_url` (str|None): Base URL for requests.
- :attr:`endpoint` (str): Endpoint path (like "/v1/chat/completions").
- :attr:`method` (Literal["get","post","put","delete"]): HTTP method.
- :attr:`openai_compatible` (bool): If True, uses an OpenAI-like calling convention.
- :attr:`is_invokeable` (bool): If True, supports direct invocation.
- :attr:`is_streamable` (bool): If True, can stream partial results.
- :attr:`requires_tokens` (bool): If True, the system calculates tokens prior to the call.
- **Other** fields: 
  - :attr:`required_kwargs`, :attr:`optional_kwargs`, :attr:`deprecated_kwargs`
  - :attr:`api_version`, :attr:`allowed_roles`
  - etc.


.. class:: EndPoint
   :synopsis: An abstract base for a particular API endpoint.

   Abstract base class that defines the interface for API endpoints.

**Key Methods**:

- :meth:`create_payload(...)` -> dict:
  Accepts request parameters and merges them with the endpoint's 
  config (like `required_kwargs`) to create a final payload + headers.
- :meth:`invoke(payload, headers, is_cached=False, **kwargs)`:
  Handles the actual or cached request.
- :meth:`_invoke(...)` (abstract):
  The core HTTP request logic (subclasses must implement).
- :meth:`_stream(...)` (abstract):
  Streaming request logic if the endpoint is streamable.
- :meth:`calculate_tokens(payload)`:
  If `requires_tokens=True`, uses :class:`TokenCalculator` to estimate 
  usage.

**Concrete Implementations**:
- :class:`ChatCompletionEndPoint` in 
  ``lionagi.service.endpoints.chat_completion.ChatCompletionEndPoint``
- Additional provider-specific classes (OpenAI, Anthropic, etc.).


-------------------------
2. TokenCalculator
-------------------------
.. module:: lionagi.service.token_calculator
   :synopsis: Logic for counting tokens or image usage.

.. class:: TokenCalculator

Methods to estimate token usage for text or images:

- :meth:`calculate_message_tokens(messages, **kwargs)` -> int:
  Sums up tokens for each message in a chat scenario.
- :meth:`calcualte_embed_token(inputs, **kwargs)` -> int:
  Summation for embedding calls.
- :meth:`tokenize(...)` -> int|list[int]:
  Generic method to tokenize a string using `tiktoken`, returning either
  token count or the token IDs themselves.


-------------------------
3. APICalling (Event)
-------------------------
.. module:: lionagi.service.endpoints.base
   :synopsis: An event representing a single API call.

.. class:: APICalling

   **Inherits from**: :class:`Event`

   An event class representing a single API call. Stores:
- :attr:`payload` (dict): Data to send in the request.
- :attr:`headers` (dict): Additional HTTP headers.
- :attr:`endpoint` (:class:`EndPoint`): The endpoint to call.
- :attr:`is_cached` (bool): Whether this call uses caching.
- :attr:`should_invoke_endpoint` (bool): If False, no actual invocation.

Implements:

- :meth:`invoke()` (async):
  The main method that performs the request, with retries if needed.
- :meth:`stream(...)` (async generator):
  If endpoint supports streaming, yields partial results.


---------------------
4. ChatCompletionEndPoint & Subclasses
---------------------
.. module:: lionagi.service.endpoints.chat_completion

.. class:: ChatCompletionEndPoint(EndPoint)

A base class for chat-style endpoints that expects role-based messages
(“system”, “user”, “assistant”, etc.). Subclasses override `_invoke()` 
and `_stream()` for each provider's specifics.

**Examples** (subclasses):
  
- :class:`OpenAIChatCompletionEndPoint`
- :class:`AnthropicChatCompletionEndPoint`
- :class:`GroqChatCompletionEndPoint`
- :class:`OpenRouterChatCompletionEndPoint`
- :class:`PerplexityChatCompletionEndPoint`

Each provider sets up its own config with required/optional fields, 
and possibly different base URLs or roles.


---------------------------
5. Rate-Limited Execution
---------------------------
.. module:: lionagi.service.endpoints.rate_limited_processor

.. class:: RateLimitedAPIProcessor

   **Inherits from**: :class:`Processor`

   A concurrency-limiting, rate-limiting processor dedicated 
   to handling :class:`APICalling` events. Supports:

   - :attr:`limit_requests` (#requests per interval).
   - :attr:`limit_tokens` (#tokens per interval).
   - :attr:`interval` (seconds) for refreshing or replenishing capacity.


.. class:: RateLimitedAPIExecutor

   **Inherits from**: :class:`Executor`

   Builds on the above **Processor**. For an iModel, it manages 
   the queued or concurrent calls.  
   **Example**:  
   One can define a queue of max capacity 100, refreshing every 60s, 
   limiting requests or tokens as needed.


----------------
6. iModel
----------------
.. module:: lionagi.service.imodel
   :synopsis: Encapsulates endpoint usage + concurrency limits.

.. class:: iModel

Represents a single “model interface” to a provider's chat or completion endpoint.
Holds:

- :attr:`endpoint` (:class:`EndPoint`):
  Typically a :class:`ChatCompletionEndPoint` or custom.
- :attr:`executor` (:class:`RateLimitedAPIExecutor`):
  A concurrency-limiting queue for calls.
- :attr:`kwargs`:
  Additional default parameters (like "model" name, "api_key", etc.).

**Methods**:

- :meth:`invoke(**kwargs) -> APICalling|None`:
  Creates an APICalling from combined endpoint config + local kwargs, 
  queues it in the executor, and awaits completion.
- :meth:`stream(**kwargs) -> APICalling|None`:
  Streams partial results if the endpoint is streamable.
- :meth:`create_api_calling(**kwargs) -> APICalling`:
  A utility to unify parameters into a final APICalling object.

**Usage**::

   from lionagi.service.imodel import iModel

   # Provide minimal config
   my_model = iModel(provider="openai", base_url="https://api.openai.com/v1", model="gpt-3.5-turbo")
   # -> Creates an endpoint automatically
   # -> Also sets up a RateLimitedAPIExecutor

   # Now we can call
   result = await my_model.invoke(messages=[{"role":"user","content":"Hello!"}])
   print(result.execution.response)


------------------
7. iModelManager
------------------
.. module:: lionagi.service.imodel

.. class:: iModelManager(Manager)

Maintains a dictionary of named :class:`iModel` objects:

- :attr:`chat`:
  The “chat” model if we define one as "chat" in the registry.
- :attr:`parse`:
  The “parse” model for secondary tasks like extracting structured data.
- :meth:`register_imodel(name, model)`:
  Insert or update the registry with a specific name.

**Example**:

   from lionagi.service.imodel import iModel, iModelManager

   chat_mod = iModel(provider="openai", model="gpt-3.5-turbo")
   parse_mod = iModel(provider="openai", model="text-davinci-003")

   manager = iModelManager(chat=chat_mod, parse=parse_mod)
   # -> manager.chat = chat_mod, manager.parse = parse_mod


-----------------
Summary
-----------------
The **LionAGI Service** system integrates everything needed to **call external 
LLM services**:

- **Endpoints** for each provider (OpenAI, Anthropic, etc.).
- **APICalling** event for tracking usage or partial streaming.
- **Rate-limiting** structures (Processor, Executor) to handle concurrency or 
  daily usage caps.
- **iModel** as a top-level convenience object: one instance = one 
  distinct provider + concurrency constraints. 
- **iModelManager** for multi-model usage in the same environment.

By configuring endpoints properly and using the **RateLimitedAPIExecutor**, 
LionAGI can handle robust multi-provider or multi-model usage while avoiding 
throttling or over-limit errors.
