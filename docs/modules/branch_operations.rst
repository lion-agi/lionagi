.. _lionagi-branch-operations:

=================================================
Branch-Level Operations
=================================================
These operations define how a :class:`~lionagi.session.branch.Branch` 
actually **does** things—ranging from direct LLM calls (`chat`, `interpret`, `communicate`) 
to advanced flows (`operate`, `instruct`, `ReAct`, etc.). Each 
is implemented as a separate function and exposed as an **asynchronous** 
method on ``Branch``.

For convenience, they can be categorized as:

- **Simple conversation**: :func:`chat`
- **Structured in-memory conversation**: :func:`communicate`, :func:`operate`, :func:`instruct`
- **Short or specialized**: :func:`interpret`, :func:`translate`
- **Action invocation**: :func:`_act`, :func:`act`
- **Selection**: :func:`select`
- **in-memory ReAct**: :func:`ReAct` for multi-step reasoning
- **Parsing**: :func:`parse` to convert text to a structured model


``_act``
--------

A **low-level** method invoked by :meth:`branch.act()`. It matches an 
action request (function + arguments) to the :class:`ActionManager` 
and executes it, returning an :class:`ActionResponseModel`. Typically 
you won't call ``_act`` directly; use :meth:`act` instead.

.. function:: _act(branch, action_request, suppress_errors=False)

    Internal method to invoke a tool (action) asynchronously.

    Parameters
    ----------
    branch : Branch
        The branch instance managing the action
    action_request : ActionRequest | BaseModel | dict
        Must contain `function` and `arguments`
    suppress_errors : bool, optional
        If True, errors are logged instead of raised

    Returns
    -------
    ActionResponseModel
        Result of the tool invocation or None if suppressed

    Notes
    -----
    This function:
    - Extracts function name and arguments from the request
    - Invokes the function through the branch's ActionManager
    - Logs the execution
    - Updates the branch's message history
    - Returns a standardized ActionResponse


``act``
-------

The *public* interface for invoking tools. Accepts a single or list 
of action requests. Optionally retries, logs errors, or merges results. 
This is best used for **explicit function calls** triggered from user 
instructions or system logic.

.. method:: Branch.act(action_request, *, suppress_errors=True, sanitize_input=False, unique_input=False, num_retries=0, initial_delay=0, retry_delay=0, backoff_factor=1, retry_default=UNDEFINED, retry_timeout=None, retry_timing=False, max_concurrent=None, throttle_period=None, flatten=True, dropna=True, unique_output=False, flatten_tuple_set=False)

    Public, potentially batched, asynchronous interface to run one or multiple action requests.

    Parameters
    ----------
    action_request : list | ActionRequest | BaseModel | dict
        A single or list of action requests, each requiring `function` and `arguments`
    suppress_errors : bool, default=True
        If True, log errors instead of raising exceptions
    sanitize_input : bool, default=False
        Reserved. Potentially sanitize the action arguments
    unique_input : bool, default=False
        Reserved. Filter out duplicate requests
    num_retries : int, default=0
        Number of times to retry on failure
    initial_delay : float, default=0
        Delay before first attempt (seconds)
    retry_delay : float, default=0
        Base delay between retries
    backoff_factor : float, default=1
        Multiplier for the retry_delay after each attempt
    retry_default : Any, default=UNDEFINED
        Fallback value if all retries fail (if suppressing errors)
    retry_timeout : float | None, default=None
        Overall timeout for all attempts (None = no limit)
    retry_timing : bool, default=False
        If True, track time used for retries
    max_concurrent : int | None, default=None
        Maximum concurrent tasks (if batching)
    throttle_period : float | None, default=None
        Minimum spacing (in seconds) between requests
    flatten : bool, default=True
        If a list of results is returned, flatten them if possible
    dropna : bool, default=True
        Remove None or invalid results from final output if True
    unique_output : bool, default=True
        Only return unique results if True
    flatten_tuple_set : bool, default=False
        Flatten nested tuples in results if True

    Returns
    -------
    Any
        The result or results from the invoked tool(s)


``chat``
--------

The fundamental LLM-based conversation method. Combines existing 
messages with a new instruction (and optional guidance/context) 
into a single prompt, sends it to the chat model, and returns 
the final :class:`AssistantResponse`. It can also produce an 
:class:`Instruction` if you set certain flags.

.. method:: Branch.chat(instruction=None, guidance=None, context=None, sender=None, recipient=None, request_fields=None, response_format=None, progression=None, imodel=None, tool_schemas=None, images=None, image_detail=None, plain_content=None, return_ins_res_message=False, **kwargs)

    Invokes the chat model with the current conversation history. This method does not
    automatically add messages to the branch. It is typically used for orchestrating.

    Parameters
    ----------
    instruction : Any, optional
        Main user instruction text or structured data
    guidance : Any, optional
        Additional system or user guidance text
    context : Any, optional
        Context data to pass to the model
    sender : Any, optional
        The user or entity sending this message (defaults to Branch.user)
    recipient : Any, optional
        The recipient of this message (defaults to self.id)
    request_fields : Any, optional
        Partial field-level validation reference
    response_format : type[BaseModel], optional
        A Pydantic model type for structured model responses
    progression : Any, optional
        Custom ordering of messages in the conversation
    imodel : iModel, optional
        An override for the chat model to use
    tool_schemas : Any, optional
        Additional schemas for tool invocation in function-calling
    images : list, optional
        Optional images relevant to the model's context
    image_detail : Literal["low", "high", "auto"], optional
        Level of detail for image-based context
    plain_content : str, optional
        Plain text content, will override any other content
    return_ins_res_message : bool, default=False
        If True, returns both Instruction and AssistantResponse objects
    **kwargs
        Additional parameters for the LLM invocation

    Returns
    -------
    tuple[Instruction, AssistantResponse] | str
        If return_ins_res_message=True, returns (Instruction, AssistantResponse)
        Otherwise returns just the response content as a string

    Notes
    -----
    High-level flow:
    1. Construct a sequence of messages from the stored progression
    2. Integrate any pending action responses into the context
    3. Invoke the chat model with the combined messages
    4. Capture and return the final response


``communicate``
---------------

Similar to :meth:`chat`, but typically used for simpler calls 
that automatically add the user query and model response to 
the conversation. It also supports optional validation into 
a Pydantic model or partial "request_fields" extraction. 
If you do not need advanced flows like action calls, 
:meth:`communicate` is a good, straightforward choice.

.. method:: Branch.communicate(instruction=None, *, guidance=None, context=None, plain_content=None, sender=None, recipient=None, progression=None, request_model=None, response_format=None, request_fields=None, imodel=None, chat_model=None, parse_model=None, skip_validation=False, images=None, image_detail="auto", num_parse_retries=3, fuzzy_match_kwargs=None, clear_messages=False, operative_model=None, **kwargs)

    A simpler orchestration than `operate()`, typically without tool invocation. Messages are 
    automatically added to the conversation.

    Parameters
    ----------
    instruction : Instruction | dict, optional
        The user's main query or data
    guidance : Any, optional
        Additional instructions or context for the LLM
    context : Any, optional
        Extra data or context
    plain_content : str, optional
        Plain text content appended to the instruction
    sender : SenderRecipient, optional
        Sender ID (defaults to Branch.user)
    recipient : SenderRecipient, optional
        Recipient ID (defaults to self.id)
    progression : ID.IDSeq, optional
        Custom ordering of messages
    request_model : type[BaseModel] | BaseModel | None, optional
        Model for validating or structuring the LLM's response
    response_format : type[BaseModel], optional
        Alias for request_model. If both are provided, raises ValueError
    request_fields : dict | list[str], optional
        If you only need certain fields from the LLM's response
    imodel : iModel, optional
        Deprecated alias for chat_model
    chat_model : iModel, optional
        An alternative to the default chat model
    parse_model : iModel, optional
        If parsing is needed, you can override the default parse model
    skip_validation : bool, optional
        If True, returns the raw response string unvalidated
    images : list, optional
        Any relevant images
    image_detail : Literal["low", "high", "auto"], default="auto"
        Image detail level (if used)
    num_parse_retries : int, default=3
        Maximum parsing retries (capped at 5)
    fuzzy_match_kwargs : dict, optional
        Additional settings for fuzzy field matching (if used)
    clear_messages : bool, optional
        Whether to clear stored messages before sending
    operative_model : type[BaseModel], optional
        Deprecated, alias for response_format
    **kwargs
        Additional arguments for the underlying LLM call

    Returns
    -------
    Any
        - Raw string (if skip_validation=True)
        - A validated Pydantic model
        - A dict of the requested fields
        - or None if parsing fails and handle_validation='return_none'

    Notes
    -----
    Flow:
    - Sends an instruction (or conversation) to the chat model
    - Optionally parses the response into a structured model or fields
    - Returns either the raw string, the parsed model, or a dict of fields


``operate``
-----------

A **robust** conversation operation that merges user instructions 
with an internal "Operative" object for structured input and output. 
It can also automatically detect requested tool calls and run them, 
then re-check or finalize the LLM output. Often used in more 
advanced scenarios where you want strong parsing or multiple 
sub-steps in the final result.

.. method:: Branch.operate(*, instruct=None, instruction=None, guidance=None, context=None, sender=None, recipient=None, progression=None, imodel=None, chat_model=None, invoke_actions=True, tool_schemas=None, images=None, image_detail=None, parse_model=None, skip_validation=False, tools=None, operative=None, response_format=None, return_operative=False, actions=False, reason=False, action_kwargs=None, field_models=None, exclude_fields=None, request_params=None, request_param_kwargs=None, response_params=None, response_param_kwargs=None, handle_validation="return_value", operative_model=None, request_model=None, **kwargs)

    Orchestrates an "operate" flow with optional tool invocation and structured response validation.
    Messages are automatically added to the conversation.

    Parameters
    ----------
    instruct : Instruct, optional
        Contains the instruction, guidance, context, etc.
    instruction : Instruction | JsonValue, optional
        The main user instruction or content for the LLM
    guidance : JsonValue, optional
        Additional system or user instructions
    context : JsonValue, optional
        Extra context data
    sender : SenderRecipient, optional
        The sender ID for newly added messages
    recipient : SenderRecipient, optional
        The recipient ID for newly added messages
    progression : Progression, optional
        Custom ordering of conversation messages
    imodel : iModel, deprecated
        Alias of chat_model
    chat_model : iModel, optional
        The LLM used for the main chat operation
    invoke_actions : bool, default=True
        If True, executes any requested tools found in the LLM's response
    tool_schemas : list[dict], optional
        Additional schema definitions for tool-based function-calling
    images : list, optional
        Optional images appended to the LLM context
    image_detail : Literal["low", "high", "auto"], optional
        The level of image detail, if relevant
    parse_model : iModel, optional
        Model used for deeper or specialized parsing
    skip_validation : bool, default=False
        If True, bypasses final validation and returns raw text
    tools : ToolRef, optional
        Tools to be registered or made available if invoke_actions is True
    operative : Operative, optional
        If provided, reuses an existing operative's config
    response_format : type[BaseModel], optional
        Expected Pydantic model for the final response
    return_operative : bool, default=False
        If True, returns the entire Operative object after processing
    actions : bool, default=False
        If True, signals that function-calling is expected
    reason : bool, default=False
        If True, signals that the LLM should provide chain-of-thought
    action_kwargs : dict, optional
        Additional parameters for the branch.act() call
    field_models : list[FieldModel], optional
        Field-level definitions or overrides for the model schema
    exclude_fields : list | dict | None, optional
        Which fields to exclude from final validation
    request_params : ModelParams, optional
        Extra config for building the request model
    request_param_kwargs : dict, optional
        Additional kwargs for ModelParams constructor
    response_params : ModelParams, optional
        Config for building the response model after actions
    response_param_kwargs : dict, optional
        Additional kwargs for response ModelParams
    handle_validation : Literal["raise", "return_value", "return_none"], default="return_value"
        How to handle parsing failures
    operative_model : type[BaseModel], deprecated
        Alias for response_format
    request_model : type[BaseModel], optional
        Another alias for response_format
    **kwargs
        Additional keyword arguments passed to branch.chat()

    Returns
    -------
    list | BaseModel | None | dict | str
        - The parsed or raw response from the LLM
        - None if validation fails and handle_validation='return_none'
        - or the entire Operative object if return_operative=True

    Raises
    ------
    ValueError
        - If both operative_model and response_format/request_model are given
        - If the LLM's response cannot be parsed and handle_validation='raise'

    Notes
    -----
    Workflow:
    1. Builds or updates an Operative object to specify how the LLM should respond
    2. Sends an instruction (instruct) or direct instruction text to branch.chat()
    3. Optionally validates/parses the result into a model or dictionary
    4. If invoke_actions=True, any requested tool calls are automatically invoked
    5. Returns either the final structure, raw response, or an updated Operative


``parse``
---------

A dedicated method for parsing raw text into a 
:class:`pydantic.BaseModel` if you do not want to incorporate 
it in the main conversation flow. Supports fuzzy matching, 
custom field handling, etc.

.. method:: Branch.parse(text, handle_validation="return_value", max_retries=3, request_type=None, operative=None, similarity_algo="jaro_winkler", similarity_threshold=0.85, fuzzy_match=True, handle_unmatched="force", fill_value=None, fill_mapping=None, strict=False, suppress_conversion_errors=False, response_format=None)

    Attempts to parse text into a structured Pydantic model using parse model logic.
    If fuzzy matching is enabled, tries to map partial or uncertain keys to the known
    fields of the model. Retries are performed if initial parsing fails.

    Parameters
    ----------
    text : str
        The raw text to parse
    handle_validation : Literal["raise", "return_value", "return_none"], default="return_value"
        What to do if parsing fails
    max_retries : int, default=3
        Number of times to retry parsing on failure
    request_type : type[BaseModel], optional
        The Pydantic model to parse into
    operative : Operative, optional
        An Operative object with known request model and settings
    similarity_algo : str, default="jaro_winkler"
        Algorithm name for fuzzy field matching
    similarity_threshold : float, default=0.85
        Threshold for matching (0.0 - 1.0)
    fuzzy_match : bool, default=True
        Whether to attempt fuzzy matching for unmatched fields
    handle_unmatched : Literal["ignore", "raise", "remove", "fill", "force"], default="force"
        Policy for unrecognized fields
    fill_value : Any, optional
        Default placeholder for missing fields (if fill is used)
    fill_mapping : dict[str, Any], optional
        A mapping of specific fields to fill values
    strict : bool, default=False
        If True, raises errors on ambiguous fields or data types
    suppress_conversion_errors : bool, default=False
        If True, logs or ignores conversion errors instead of raising
    response_format : type[BaseModel], optional
        Alternative to request_type for specifying model format

    Returns
    -------
    BaseModel | dict | str | None
        Parsed model instance, or a fallback based on handle_validation

    Raises
    ------
    ValueError
        If parsing fails and handle_validation="raise"

    Notes
    -----
    Flow:
    1. Attempts to parse text directly into model
    2. If fails, uses parse_model to reformat text
    3. Applies fuzzy matching if enabled
    4. Returns parsed model or fallback based on handle_validation


``instruct``
------------

Provides a **mid-level** approach: if your user instructions 
(wrapped in :class:`Instruct`) indicate advanced features 
(like actions, or a custom structured response), 
it calls :meth:`operate` internally. Otherwise, 
it calls :meth:`communicate`. Best for single-turn instructions 
that may or may not trigger advanced logic.

.. method:: Branch.instruct(instruct, /, **kwargs)

    A convenience method that chooses between operate() and communicate()
    based on the contents of an Instruct object.

    Parameters
    ----------
    instruct : Instruct
        An object containing instruction, guidance, context, etc.
    **kwargs
        Additional args forwarded to operate() or communicate()

    Returns
    -------
    Any
        The result of the underlying call (structured object, raw text, etc.)

    Notes
    -----
    Decision Logic:
    - If the Instruct indicates tool usage or advanced response format,
      operate() is used
    - Otherwise, defaults to communicate()

    The method examines reserved keywords in the Instruct object to determine
    which underlying method to call. This provides a simpler interface when
    you're not sure if advanced features will be needed.


``interpret``
-------------

Rewrites or refines user input into a more structured, 
explicit prompt. Useful if the user's original text might 
be ambiguous or suboptimal for the LLM. It does not store 
messages into the conversation by default.

.. method:: Branch.interpret(text, domain=None, style=None, **kwargs)

    Interprets (rewrites) a user's raw input into a more formal or structured
    LLM prompt. This function can be seen as a "prompt translator," which
    ensures the user's original query is clarified or enhanced for better
    LLM responses.

    Parameters
    ----------
    text : str
        The raw user input or question that needs interpreting
    domain : str, optional
        Optional domain hint (e.g. "finance", "marketing", "devops")
        The LLM can use this hint to tailor its rewriting approach
    style : str, optional
        Optional style hint (e.g. "concise", "detailed")
    **kwargs
        Additional arguments passed to branch.chat()

    Returns
    -------
    str
        A refined or "improved" user prompt string, suitable for feeding
        back into the LLM as a clearer instruction

    Notes
    -----
    The method calls branch.chat() behind the scenes with a system prompt
    that instructs the LLM to rewrite the input. By default, it uses a low
    temperature (0.1) to encourage consistent, focused rewrites.

    Example
    -------
    >>> refined = await interpret(
    ...     text="How do I do marketing analytics?",
    ...     domain="marketing",
    ...     style="detailed"
    ... )
    # refined might be "Explain step-by-step how to set up a marketing analytics
    #  pipeline to track campaign performance..."


``ReAct``
---------

Implements a multi-step "**reason + act**" approach, where 
the LLM is asked for chain-of-thought or intermediate steps 
that might require additional expansions. Once the chain-of-thought 
is complete, a final answer is produced. 
Optionally repeats expansions if "extension_needed" is signaled, 
up to a specified limit. Typically used in complex tasks.

.. method:: Branch.ReAct(instruct, interpret=False, tools=None, tool_schemas=None, response_format=None, extension_allowed=False, max_extensions=None, response_kwargs=None, return_analysis=False, analysis_model=None, **kwargs)

    Performs a multi-step "ReAct" flow (inspired by the ReAct paradigm in LLM usage),
    which may include chain-of-thought analysis, multiple expansions, and tool usage.

    Parameters
    ----------
    instruct : Instruct | dict[str, Any]
        The user's instruction object or a dict with equivalent keys
    interpret : bool, default=False
        If True, first interprets (branch.interpret) the instructions
    tools : Any, optional
        Tools to be made available for the ReAct process. If omitted,
        defaults to True (all tools)
    tool_schemas : Any, optional
        Additional or custom schemas for tools if function calling is needed
    response_format : type[BaseModel] | BaseModel, optional
        The final schema for the user-facing output after ReAct expansions
    extension_allowed : bool, default=False
        Whether to allow multiple expansions if analysis indicates more steps
    max_extensions : int, optional
        The max number of expansions if extension_allowed is True
    response_kwargs : dict, optional
        Extra kwargs passed into the final communicate() call
    return_analysis : bool, default=False
        If True, returns both final output and list of analysis objects
    analysis_model : iModel, optional
        A custom LLM model for generating the ReAct analysis steps
    **kwargs
        Additional keyword arguments passed into the initial operate() call

    Returns
    -------
    Any | tuple[Any, list]
        - If return_analysis=False, returns only the final output
        - If return_analysis=True, returns (final_output, list_of_analyses)

    Notes
    -----
    Flow:
    1. Optionally interprets the user instruction
    2. Generates chain-of-thought analysis using a specialized schema
    3. Optionally expands conversation if analysis indicates more steps
    4. Produces final answer by invoking branch.communicate()

    - Messages are automatically added to the branch context
    - If max_extensions > 5, it is clamped to 5 with a warning
    - The expansions loop continues until either analysis.extension_needed
      is False or extensions (remaining allowed expansions) is 0


``select``
----------

A convenience operation for letting the LLM choose one or more 
items from a given list or dictionary. For instance, if you have 
10 possible solutions and want the model to pick the best one(s). 
Returns a structured "selection model" describing which was chosen.

.. method:: Branch.select(instruct, choices, max_num_selections=1, branch_kwargs=None, return_branch=False, verbose=False, **kwargs)

    Performs a selection operation from given choices using an LLM-driven approach.

    Parameters
    ----------
    instruct : Instruct | dict[str, Any]
        The instruction model or dictionary for the LLM call
    choices : list[str] | type[Enum] | dict[str, Any]
        The set of options to choose from
    max_num_selections : int, default=1
        Maximum allowed selections
    branch_kwargs : dict[str, Any], optional
        Extra arguments to create or configure a new branch if needed
    return_branch : bool, default=False
        If True, returns both selection result and branch instance
    verbose : bool, default=False
        If True, prints debug info
    **kwargs
        Additional arguments for the underlying operate() call

    Returns
    -------
    SelectionModel | tuple[SelectionModel, Branch]
        - A SelectionModel containing the chosen items
        - If return_branch=True, also returns the branch instance

    Notes
    -----
    Flow:
    1. Parses choices into a consistent representation
    2. Creates a selection prompt with the choices
    3. Uses branch.operate() to get LLM's selection
    4. Validates and corrects the selections
    5. Returns result in a structured SelectionModel


``translate``
-------------

A specialized method for transforming text with a given 
"technique" (currently "SynthLang"), optionally compressing 
the result. This is a demonstration of hooking up 
domain-specific transformations in a single step.

.. method:: Branch.translate(text, technique="SynthLang", technique_kwargs=None, compress=False, chat_model=None, compress_model=None, compression_ratio=0.2, compress_kwargs=None, verbose=True, new_branch=True, **kwargs)

    Transform text using a chosen technique (currently only "SynthLang").
    Optionally compresses text with a custom compress_model.

    Parameters
    ----------
    text : str
        The text to be translated or transformed
    technique : Literal["SynthLang"], default="SynthLang"
        The translation/transform technique
    technique_kwargs : dict, optional
        Additional parameters for the chosen technique
    compress : bool, default=False
        Whether to compress the resulting text further
    chat_model : iModel, optional
        A custom model for the translation step
    compress_model : iModel, optional
        A separate model for compression (if compress=True)
    compression_ratio : float, default=0.2
        Desired compression ratio if compressing text (0.0 - 1.0)
    compress_kwargs : dict, optional
        Additional arguments for the compression step
    verbose : bool, default=True
        If True, prints debug/logging info
    new_branch : bool, default=True
        If True, performs the translation in a new branch context
    **kwargs
        Additional parameters passed through to the technique function

    Returns
    -------
    str
        The transformed (and optionally compressed) text

    Raises
    ------
    ValueError
        If an unsupported technique is specified

    Notes
    -----
    Currently only supports the "SynthLang" technique, which uses a
    symbolic systems template by default. The compression step is optional
    and can be configured with its own model and parameters.


Differences and Usage Notes
---------------------------
- **chat** vs. **communicate**:
  - ``chat`` is more manual: you supply how the conversation 
    is built, and it returns an :class:`AssistantResponse`. 
    It does **not** automatically store those messages unless you do so.  
  - ``communicate`` is simpler: it automatically adds new messages 
    (user + response) to the conversation, optionally validates 
    the LLM output with a pydantic model or partial fields.

- **operate** vs. **instruct**:
  - ``operate`` is an advanced, multi-step approach with an 
    internal “Operative” model. It can parse a structured response 
    and run any requested tool calls.  
  - ``instruct`` is a simpler convenience method that decides 
    between “communicate” or “operate” based on the user's 
    :class:`Instruct` contents.

- **ReAct**:
  - A subset of advanced usage where the model is expected to 
    produce chain-of-thought or partial reasoning steps that 
    may loop if it finds it needs further expansions.

- **_act** vs. **act**:
  - ``_act`` is an internal helper that does the actual invocation 
    of a tool, returning an :class:`ActionResponse`.  
  - ``act`` is the user-facing method for one or multiple 
    function calls, supporting concurrency, error suppression, 
    or basic retry logic.

- **interpret**:
  - Focused on rewriting or “polishing” user text into a more 
    formal/explicit prompt. Doesn't store new messages.

- **parse**:
  - Takes a final text and converts it to a pydantic model or 
    dictionary. Usually used if you need structured data from 
    a raw LLM response but don't want that to be part of the 
    conversation.  

In practice, these operations can be freely combined to build 
complex pipelines—**for example**, you might 
:func:`interpret` the user input, then :func:`operate`, 
then parse final results or call custom logic.

----

File References
---------------
These operations are scattered in files (like `_act.py`, 
`chat.py`, `communicate.py`, etc.), but each is also exposed 
directly as a method on :class:`~lionagi.session.branch.Branch`.

``_act`` -> ``lionagi.operations._act.act._act``  
``chat`` -> ``lionagi.operations.chat.chat``  
``communicate`` -> ``lionagi.operations.communicate.communicate``  
``operate`` -> ``lionagi.operations.operate.operate``  
``parse`` -> ``lionagi.operations.parse.parse``  
``instruct`` -> ``lionagi.operations.instruct.instruct``  
``interpret`` -> ``lionagi.operations.interpret.interpret``  
``ReAct`` -> ``lionagi.operations.ReAct.ReAct``  
``select`` -> ``lionagi.operations.select.select``  
``translate`` -> ``lionagi.operations.translate.translate``

``act`` is simply a method in 
``lionagi.session.branch.Branch.act`` that calls 
``_act`` for each request.

``Branch`` itself is documented separately in 
:ref:`lionagi-branch-class`.

----

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
