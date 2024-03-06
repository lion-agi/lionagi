
# Mono Workflow Management

This documentation provides details on the classes and methods designed for managing chat flows, conversations with Large Language Models (LLMs), and tool invocation within the Lionagi framework.

## BaseMonoFlow

The foundational class for creating mono-directional flows within applications.

### Constructor

- `__init__(branch)`: Initializes a new instance of `BaseMonoFlow` with a specified [[Branch]].

  - `branch`: The branch instance to be used for chat operations.

### Class Methods

- `class_name() -> str`: Returns the name of the class.

## MonoChat

Extends `BaseMonoFlow` to specifically handle chat completions and interactions in a conversational context.

### Constructor

- Inherits the constructor from `BaseMonoFlow`.

### Methods

#### process_chatcompletion

- Processes the outcome of a chat completion request.

  - [[API Utilities#^438814|payload]]: The input data for the chat completion.
  - `completion`: The response from the chat completion.
  - `sender`: Identifies the sender of the chat message.

#### call_chatcompletion

- Asynchronously calls the chat completion [[Base Service|service]] and processes the outcome.

  - `sender`: Optionally specifies the sender of the chat message.
  - `with_sender`: Determines if sender information should be included in chat messages.
  - `**kwargs`: Additional keyword arguments for the chat service.

#### chat

- Initiates and handles a chat conversation, potentially involving instructions, system messages, and tool invocations.

  - `instruction`: The chat instruction, either as a `Instruction` object or a string.
  - `context`: Additional context for the chat.
  - `sender`: Specifies the sender of the chat message.
  - `system`: System message to process alongside the chat.
  - `tools`: Indicates tools to invoke as part of the chat.
  - `out`: Controls output of the chat response.
  - `invoke`: Determines if tools should be invoked during the chat.
  - `**kwargs`: Arbitrary keyword arguments for further customization.

### Advanced Chat Interaction Methods

#### ReAct

- Manages a sequence of chat interactions with follow-up actions, applying reasoning and action planning.

  - `instruction`: Instruction for the initial chat.
  - `context`: Additional context for the chat.
  - `sender`: Sender of the chat message.
  - `system`: System message to include.
  - `tools`: Specifies tools for invocation.
  - `num_rounds`: Number of follow-up rounds to execute.
  - `**kwargs`: Additional configurations for the chat.

#### auto_followup

- Automates follow-up interactions based on the outcome of previous chats and tool invocations.

  - `instruction`: Instruction for the chat.
  - `context`: Contextual information for the chat.
  - `sender`: Sender of the chat message.
  - `system`: System message to process.
  - `tools`: Tools to be invoked as part of the follow-up.
  - `max_followup`: Maximum number of follow-up chats allowed.
  - `out`: Determines if the final result should be output.
  - `**kwargs`: Additional configurations for the follow-up interactions.

#### followup

- Facilitates manual follow-up chats with tool invocation, designed for more controlled interaction sequences.

  - `instruction`: The chat instruction.
  - `context`: Context for the chat.
  - `sender`: Identifies the sender.
  - `system`: System message for processing.
  - `tools`: Tools to invoke during the follow-up.
  - `max_followup`: Maximum number of follow-up interactions.
  - `out`: Controls output of the final result.
  - `**kwargs`: Additional configurations for follow-up chats.

