
# LionAGI Session Tutorial

## Introduction

This tutorial introduces the `Session` class in the LionAGI framework, which facilitates creating and managing conversational sessions with various functionalities. This guide will cover creating sessions, interacting with the chat interface, retrieving responses, and using external tools through LionAGI's `Session` class.

## Table of Contents

1. [Setting Up the Session](#setting-up-the-session)
2. [Chat Interaction](#chat-interaction)
3. [Splitting Branches](#splitting-branches)
4. [Working with Tools](#working-with-tools)
5. [Reviewing Metadata](#reviewing-metadata)
6. [Sending Messages](#sending-messages)
7. [Conclusion](#conclusion)

## Setting Up the Session

To start, you need to import the necessary modules from the LionAGI package and create an instance of the `Session` class.

### Example Usage

The following code demonstrates how to import LionAGI and create a `Session` instance.

```python
from lionagi import Session

# Create a Session instance with a specified system message
session = Session(system="As a comedian, you are sarcastically funny")
```

## Chat Interaction

Once you have a `Session` instance, you can interact with the chat interface by inputting a message and awaiting the response.

### Example Usage

The following code demonstrates how to input a chat message and await a response.

```python
# Input a chat message and await a response
await session.branches[0].chat(
    "very short joke: a blue whale and a big shark meet at the bar and start dancing"
)
# Output: 'A blue whale and a big shark meet at the bar and start dancing. The bartender says, "Great, now I need a bigger dance floor and a mop!"'
```

## Splitting Branches

You can split a branch within a session to create a new conversational path while preserving the current context.

### Example Usage

The following code demonstrates how to split a branch and inspect the new branch.

```python
# Split the current branch
session.split_branch(session.branches[0])

# Inspect the new branch
session.branches[1].to_df()
```

## Working with Tools

The `Session` class allows you to define and use external tools for more complex interactions. You can define a tool, such as a calculator function, and invoke it within a chat interaction.

### Example Usage

The following code demonstrates how to define a multiplication tool and use it in a chat interaction.

```python
def multiply(number1: float, number2: float):
    """
    Perform multiplication on two numbers.

    Args:
        number1: First number to multiply.
        number2: Second number to multiply.

    Returns:
        The product of number1 and number2.
    """
    return number1 * number2

from lionagi.core.action import func_to_tool

# Convert the function to a tool
tool_m = func_to_tool(multiply)

# Create a new branch with the tool
session.new_branch(
    system="you are asked to perform as a function picker and parameter provider"
)

# Example questions to solve
question1 = "A school is ordering laptops for its students. If each classroom has 25 students and the school wants to provide a laptop for each student in its 8 classrooms, how many laptops in total does the school need to order?"
question2 = "A bakery sells cupcakes in boxes of 6. If a customer wants to buy 8 boxes, with each person getting one cupcake, how many people can the customer serve cupcake to?"

import json

context = {"Question1": question1, "question2": question2}
context = json.dumps(context)

# Send the instruction and context, and await the response
result = await session.branches[2].direct(
    instruction="Think step by step, understand the following basic math question and provide parameters for function calling.",
    context=context,
    tools=tool_m,
    reason=True,
    score=True,
)
```

## Reviewing Metadata

You can inspect the metadata associated with each message to get additional details about the interaction, such as timestamps and usage statistics.

### Example Usage

The following code demonstrates how to inspect the metadata of messages.

```python
# Convert messages to a DataFrame for inspection
session.branches[0].to_df()

# Inspect metadata of a specific message
session.branches[0].messages[1].metadata
```

The metadata provides information about the sender, recipient, timestamps, and additional details relevant to the interaction.

## Sending Messages

You can send messages, tools, or models from one branch to another within the same session.

### Example Usage

The following code demonstrates how to send a message from one branch to another.

```python
# Get the last message from the source branch
last_message = session.branches[1].messages[-1]

# Send the message to the target branch
session.branches[1].send(
    recipient=session.branches[0].ln_id,
    category="message",
    package=last_message,
)

# Collect and process all sent and received messages
session.collect_send_all(receive_all=True)
```

## Conclusion

In this tutorial, we covered the basics of using the `Session` class from the LionAGI framework, including setting up a session, interacting with the chat interface, splitting branches, handling responses, working with external tools, reviewing metadata, and sending messages. By understanding these functionalities, you can effectively manage complex conversational interactions and integrate external tools within your LionAGI-based systems.
