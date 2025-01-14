.. _lionagi-messages:

====================================================
Messages Subsystem
====================================================
.. module:: lionagi.protocols.messages
   :synopsis: Classes for instructions, AI responses, action requests/responses, and system-level messages.

Overview
--------
This subsystem handles **structured messages** in LionAGI, enabling:
- **User instructions** (with context, images, or tool references),
- **System** messages that define context or constraints,
- **Assistant** responses capturing AI output,
- **ActionRequests** and **ActionResponses** to call code or tools.

All are subclasses of :class:`RoledMessage`, which defines a *role*, *sender*, *recipient*, and *content*.

Contents
--------
.. contents::
   :local:
   :depth: 2


Base Types
----------
.. _lionagi-messages-base:

.. module:: lionagi.protocols.messages.base

    Holds foundational enumerations and types for messages, including roles like SYSTEM, USER, and helper functions for validating sender/recipient fields.

    Key enumerations like :class:`MessageRole` (``SYSTEM``, ``USER``, ``ASSISTANT``, etc.) and the basic notion of a "sender/recipient" reside here.

.. class:: MessageRole(str, Enum)

    Predefined roles for conversation participants or message semantics.

    Members
    -------
    SYSTEM : str
        System-level message role
    USER : str
        User message role
    ASSISTANT : str
        Assistant (AI) message role
    UNSET : str
        Unset or default role
    ACTION : str
        Action-related message role

.. class:: MessageFlag(str, Enum)

    Internal flags for certain message states, e.g., clones or loads.

    Members
    -------
    MESSAGE_CLONE : str
        Flag indicating a cloned message
    MESSAGE_LOAD : str
        Flag indicating a loaded message

.. class:: MessageField(str, Enum)

    Common field names used in message objects.

    Members
    -------
    CREATED_AT : str
        Field name for creation timestamp
    ROLE : str
        Field name for message role
    CONTENT : str
        Field name for message content
    ID : str
        Field name for message ID
    SENDER : str
        Field name for message sender
    RECIPIENT : str
        Field name for message recipient
    METADATA : str
        Field name for message metadata

.. data:: SenderRecipient

    A union type indicating that a sender or recipient could be:
    - A lionagi IDType
    - A string-based role or ID
    - A specific enum role from MessageRole

.. data:: MESSAGE_FIELDS

    List of all common message field names from MessageField enum.

.. function:: validate_sender_recipient(value)

    Normalize a sender/recipient value into a recognized type.

    Parameters
    ----------
    value : Any
        Input to interpret as a role or ID

    Returns
    -------
    SenderRecipient
        A validated and normalized entity

    Raises
    ------
    ValueError
        If the input cannot be recognized as a role or ID


RoledMessage
------------
.. _lionagi-messages-message:

.. module:: lionagi.protocols.messages.message

    Implements the RoledMessage base for system, user, assistant, and action messages, plus Jinja2 environment and template loading.

    Defines a general base class for typed messages with a **role**. Every specialized message (like system instructions, user instructions, or AI responses) inherits from :class:`RoledMessage`.

.. class:: RoledMessage(Node, Sendable)

    A base class for all messages that have a role and carry structured content. Subclasses might be Instruction, ActionRequest, etc.

    Attributes
    ----------
    content : dict
        The content of the message
    role : MessageRole | None
        The role of the message in the conversation
    template : str | Template | None
        Optional Jinja template for rendering content
    sender : SenderRecipient | None
        The ID of the sender node or a role
    recipient : SenderRecipient | None
        The ID of the recipient node or a role

    Properties
    ----------
    image_content : list[dict[str, Any]] | None
        Extract structured image data from the message content if it is represented as a chat message array
    chat_msg : dict[str, Any] | None
        A dictionary representation typically used in chat-based contexts
    rendered : str
        Attempt to format the message with a Jinja template (if provided)

    Methods
    -------
    create(**kwargs)
        Must be implemented in subclass to create new instances

    from_dict(dict_)
        Deserialize a dictionary into a RoledMessage or subclass

    is_clone()
        Check if this message is flagged as a clone

    clone(keep_role=True)
        Create a shallow copy of this message, possibly resetting the role

    to_log()
        Convert this message into a Log, preserving all current fields

    update(sender, recipient, template, **kwargs)
        Generic update mechanism for customizing the message in place

    Notes
    -----
    The RoledMessage class is designed to be subclassed by specific message types like System, Instruction, etc. 
    It provides template-based rendering of content and serialization support for various field types.


System
------
.. module:: lionagi.protocols.messages.system

    Defines the System class, representing system-level instructions or settings that guide the AI's behavior from a privileged role.

    :class:`System` sets *system-level* instructions. Typically the very first message in a conversation, it describes how the AI should behave overall.

.. class:: System(RoledMessage)

    A specialized message that sets a system-level context or policy. Usually the first in a conversation, instructing the AI about general constraints or identity.

    Attributes
    ----------
    template : str | Template | None
        Template for rendering system messages, defaults to system_message.jinja2

    Methods
    -------
    create(system_message="You are a helpful AI assistant. Let's think step by step.", system_datetime=None, sender=None, recipient=None, template=None, system=None, **kwargs)
        Construct a system message with optional datetime annotation

        Parameters
        ----------
        system_message : str
            The main text instructing the AI about behavior/identity
        system_datetime : bool | str, optional
            If True or str, embed a time reference. If str, it is used directly
        sender : SenderRecipient, optional
            Typically MessageRole.SYSTEM
        recipient : SenderRecipient, optional
            Typically MessageRole.ASSISTANT
        template : Template | str | None
            An optional custom template for rendering
        system : Any
            Alias for system_message (deprecated)
        **kwargs
            Additional content merged into the final dict

        Returns
        -------
        System
            A newly created system-level message

    update(system_message=None, sender=None, recipient=None, system_datetime=None, template=None, **kwargs)
        Adjust fields of this system message

        Parameters
        ----------
        system_message : JsonValue
            New system message text
        sender : SenderRecipient
            Updated sender or role
        recipient : SenderRecipient
            Updated recipient or role
        system_datetime : bool | str
            If set, embed new datetime info
        template : Template | str | None
            New template override
        **kwargs
            Additional fields for self.content

    Notes
    -----
    The System class is designed to be the first message in a conversation, setting up the context and behavior expectations for the AI. It supports datetime annotations and custom templates for rendering the system message.


Instruction
-----------
.. module:: lionagi.protocols.messages.instruction

    Defines the Instruction class, representing user commands or instructions sent to the system. Supports optional context, images, and schema requests.

    :class:`Instruction` captures the **user's** command or question. It may contain optional context or images, as well as a schema for structured responses.

.. class:: Instruction(RoledMessage)

    A user-facing message that conveys commands or tasks. It supports optional images, tool references, and schema-based requests.

    Properties
    ----------
    guidance : str | None
        Optional guiding text for the instruction
    instruction : JsonValue | None
        The main instruction or command
    context : JsonValue | None
        Additional context about the environment
    tool_schemas : JsonValue | None
        Extra data describing available tools
    plain_content : str | None
        Raw plain text fallback
    image_detail : Literal["low", "high", "auto"] | None
        Detail level for included images
    images : list
        List of images associated with the instruction
    request_fields : dict | None
        Fields requested in the response
    response_format : type[BaseModel] | None
        Pydantic model for structured responses
    respond_schema_info : dict | None
        Schema information for responses
    request_response_format : str | None
        Formatted request response template

    Methods
    -------
    create(instruction=None, *, context=None, guidance=None, images=None, sender=None, recipient=None, request_fields=None, plain_content=None, image_detail=None, request_model=None, response_format=None, tool_schemas=None)
        Construct a new Instruction

    extend_images(images, image_detail=None)
        Append images to the existing list

    extend_context(*args, **kwargs)
        Append additional context to the existing context array

    update(*, guidance=None, instruction=None, context=None, request_fields=None, plain_content=None, request_model=None, response_format=None, images=None, image_detail=None, tool_schemas=None, sender=None, recipient=None)
        Batch-update this Instruction

    Notes
    -----
    The Instruction class is designed to be flexible in how it represents user commands, supporting 
    everything from simple text instructions to complex requests with images, schemas, and tool references.


AssistantResponse
-----------------
.. module:: lionagi.protocols.messages.assistant_response

    Defines AssistantResponse, a specialized RoledMessage for the AI's assistant replies (usually from LLM or related).

    :class:`AssistantResponse` is the AI's reply to a user or system message. This may store raw model data (JSON output) in ``metadata["model_response"]``.

.. class:: AssistantResponse(RoledMessage)

    A message representing the AI assistant's reply, typically from a model or LLM call. If the raw model output is available, it's placed in metadata["model_response"].

    Attributes
    ----------
    template : Template | str | None
        Template for rendering assistant responses, defaults to assistant_response.jinja2

    Properties
    ----------
    response : str
        Get or set the text portion of the assistant's response
    model_response : dict | list[dict]
        Access the underlying model's raw data, if available

    Methods
    -------
    create(assistant_response, sender=None, recipient=None, template=None, **kwargs)
        Build an AssistantResponse from arbitrary assistant data

        Parameters
        ----------
        assistant_response : BaseModel | list[BaseModel] | dict | str | Any
            A pydantic model, list, dict, or string representing an LLM or system response
        sender : SenderRecipient | None
            The ID or role denoting who sends this response
        recipient : SenderRecipient | None
            The ID or role to receive it
        template : Template | str | None
            Optional custom template
        **kwargs
            Additional content key-value pairs

        Returns
        -------
        AssistantResponse
            The constructed instance

    update(assistant_response=None, sender=None, recipient=None, template=None, **kwargs)
        Update this AssistantResponse with new data or fields

        Parameters
        ----------
        assistant_response : BaseModel | list[BaseModel] | dict | str | Any
            Additional or replaced assistant model output
        sender : SenderRecipient | None
            Updated sender
        recipient : SenderRecipient | None
            Updated recipient
        template : Template | str | None
            Optional new template
        **kwargs
            Additional content updates for self.content

    Notes
    -----
    The AssistantResponse class is designed to handle various formats of AI model outputs, from simple 
    strings to complex structured responses. It preserves both the human-readable response and the raw 
    model output when available.


ActionRequest
-------------
.. module:: lionagi.protocols.messages.action_request

    Defines the ActionRequest class, a specific RoledMessage for requesting a function or action call within LionAGI. It is typically accompanied by arguments and can later be answered by an ActionResponse.

    :class:`ActionRequest` is a special message for requesting a function call or action. Contains a function name and arguments.

.. class:: ActionRequest(RoledMessage)

    A message that requests an action or function to be executed. It inherits from RoledMessage and includes function name, arguments, and optional linking to a subsequent ActionResponse.

    Attributes
    ----------
    template : Template | str | None
        Template for rendering action requests, defaults to action_request.jinja2

    Properties
    ----------
    action_response_id : IDType | None
        Get or set the ID of the corresponding action response
    request : dict[str, Any]
        Get the entire 'action_request' dictionary if present
    arguments : dict[str, Any]
        Access just the 'arguments' from the action request
    function : str
        Name of the function to be invoked

    Methods
    -------
    create(function=None, arguments=None, sender=None, recipient=None, template=None, **kwargs)
        Build a new ActionRequest

        Parameters
        ----------
        function : str | Callable | None
            The function or callable name
        arguments : dict | None
            Arguments for that function call
        sender : SenderRecipient | None
            The sender identifier or role
        recipient : SenderRecipient | None
            The recipient identifier or role
        template : Template | str | None
            Optional custom template
        **kwargs
            Extra key-value pairs to merge into the content

        Returns
        -------
        ActionRequest
            A newly constructed instance

    update(function=None, arguments=None, sender=None, recipient=None, action_response=None, template=None, **kwargs)
        Update this request with new function, arguments, or link to an action response

        Parameters
        ----------
        function : str
            New function name, if changing
        arguments : dict
            New arguments dictionary, if changing
        sender : SenderRecipient
            New sender
        recipient : SenderRecipient
            New recipient
        action_response : ActionResponse
            If provided, this request is flagged as responded
        template : Template | str | None
            Optional new template
        **kwargs
            Additional fields to store in content

        Raises
        ------
        ValueError
            If the request is already responded to

    is_responded()
        Check if there's a linked action response

        Returns
        -------
        bool
            True if an action response ID is present

    Notes
    -----
    The ActionRequest class is designed to represent function or action calls within the system. 
    It maintains a link to its corresponding ActionResponse once the action is completed.


ActionResponse
--------------
.. module:: lionagi.protocols.messages.action_response

    Defines ActionResponse, an RoledMessage that answers an ActionRequest with output from a function call or action.

    Pairs with an :class:`ActionRequest`, providing the **output** of that requested function. The original request ID is also tracked.

.. class:: ActionResponse(RoledMessage)

    A message fulfilling an ActionRequest. It stores the function name, the arguments used, and the output produced by the function.

    Attributes
    ----------
    template : Template | str | None
        Template for rendering action responses, defaults to action_response.jinja2

    Properties
    ----------
    function : str
        Name of the function that was executed
    arguments : dict[str, Any]
        Arguments used for the executed function
    output : Any
        The result or returned data from the function call
    response : dict[str, Any]
        A helper to get the entire 'action_response' dictionary
    action_request_id : IDType
        The ID of the original action request

    Methods
    -------
    create(action_request, output=None, response_model=None, sender=None, recipient=None)
        Build an ActionResponse from a matching ActionRequest and output

        Parameters
        ----------
        action_request : ActionRequest
            The original request being fulfilled
        output : Any, optional
            The function output or result
        response_model : Any, optional
            If present and has .output, this is used instead of output
        sender : SenderRecipient, optional
            The role or ID of the sender (defaults to the request's recipient)
        recipient : SenderRecipient, optional
            The role or ID of the recipient (defaults to the request's sender)

        Returns
        -------
        ActionResponse
            A new instance referencing the ActionRequest

    update(action_request=None, output=None, response_model=None, sender=None, recipient=None, template=None, **kwargs)
        Update this response with a new request reference or new output

        Parameters
        ----------
        action_request : ActionRequest
            The updated request
        output : Any
            The new function output data
        response_model : Any
            If present, uses response_model.output
        sender : SenderRecipient
            New sender ID or role
        recipient : SenderRecipient
            New recipient ID or role
        template : Template | str | None
            Optional new template
        **kwargs
            Additional fields to store in content

    Notes
    -----
    The ActionResponse class is designed to pair with ActionRequest messages, providing a structured way 
    to return function call results while maintaining the link to the original request.


MessageManager
--------------
.. module:: lionagi.protocols.messages.manager

    Implements the MessageManager class, a manager for collecting or manipulating sequences of RoledMessage objects, including system, instructions, or action requests/responses.

    A manager for collecting messages in order, offering utility methods to add system instructions, user instructions, or assistant responses, and to fetch them (e.g. "last instruction"). Also includes **action** request/response handling.

.. class:: MessageManager(Manager)

    A manager maintaining an ordered list of RoledMessage items. Capable of setting or replacing a system message, adding instructions, assistant responses, or actions, and retrieving them conveniently.

    Properties
    ----------
    progression : Progression
        Access to the underlying progression of messages
    last_response : AssistantResponse | None
        Retrieve the most recent AssistantResponse
    last_instruction : Instruction | None
        Retrieve the most recent Instruction
    assistant_responses : Pile[AssistantResponse]
        All AssistantResponse messages in the manager
    actions : Pile[ActionRequest | ActionResponse]
        All action messages in the manager
    action_requests : Pile[ActionRequest]
        All ActionRequest messages in the manager
    action_responses : Pile[ActionResponse]
        All ActionResponse messages in the manager
    instructions : Pile[Instruction]
        All Instruction messages in the manager

    Methods
    -------
    set_system(system)
        Replace or set the system message. If one existed, remove it.

    aclear_messages()
        Async clear all messages except system.

    a_add_message(**kwargs)
        Add a message asynchronously with a manager-level lock.

    create_instruction(*, instruction=None, context=None, guidance=None, images=None, request_fields=None, plain_content=None, image_detail=None, request_model=None, response_format=None, tool_schemas=None, sender=None, recipient=None)
        Construct or update an Instruction message with advanced parameters.

    create_assistant_response(*, sender=None, recipient=None, assistant_response=None, template=None, template_context=None)
        Build or update an AssistantResponse.

    create_action_request(*, sender=None, recipient=None, function=None, arguments=None, action_request=None, template=None, template_context=None)
        Build or update an ActionRequest.

    create_action_response(*, action_request, action_output=None, action_response=None, sender=None, recipient=None)
        Create or update an ActionResponse, referencing a prior ActionRequest.

    create_system(*, system=None, system_datetime=None, sender=None, recipient=None, template=None, template_context=None)
        Create or update a System message.

    add_message(**kwargs)
        The central method to add a new message of various types.

    clear_messages()
        Remove all messages except the system message if it exists.

    remove_last_instruction_tool_schemas()
        Convenience method to strip 'tool_schemas' from the most recent Instruction.

    concat_recent_action_responses_to_instruction(instruction)
        Example method to merge the content of recent ActionResponses into an instruction's context.

    to_chat_msgs(progression=None)
        Convert a subset (or all) of messages into a chat representation array.

    Parameters
    ----------
    messages : list[RoledMessage] | None
        Initial list of messages to manage
    progression : Progression | None
        Optional custom progression to use
    system : System | None
        Optional system message to start with

    Notes
    -----
    The MessageManager class provides a central point for managing all types of messages in a conversation, 
    including system messages, instructions, responses, and action requests/responses. It maintains message 
    order and provides convenient access methods.


Example Usage
-------------
.. code-block:: python

   from lionagi.protocols.messages.message_manager import MessageManager
   from lionagi.protocols.messages.system import System
   from lionagi.protocols.messages.instruction import Instruction
   from lionagi.protocols.messages.assistant_response import AssistantResponse

   # 1) Create a manager
   manager = MessageManager(system=System.create())

   # 2) Add a user instruction
   instruct = Instruction.create(instruction="How to deploy a python app?")
   msg, _ = manager.add_message(instruction=instruct)
   
   # 3) AI responds
   response = AssistantResponse.create("You can use Docker or a PaaS like Heroku.")
   msg, _ = manager.add_message(assistant_response=response)

   # Inspect
   print(manager.last_response.response)
   # -> "You can use Docker or a PaaS like Heroku."


File Locations
--------------
- **base.py**: Shared role/flag definitions.  
- **message.py**: The :class:`RoledMessage` base class + jinja environment.  
- **system.py**: The :class:`System` specialized message.  
- **instruction.py**: The :class:`Instruction` specialized message.  
- **assistant_response.py**: The :class:`AssistantResponse` specialized message.  
- **action_request.py**: The :class:`ActionRequest` specialized message.  
- **action_response.py**: The :class:`ActionResponse` specialized message.  
- **message_manager.py**: A manager class for storing and operating on multiple messages.

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``
