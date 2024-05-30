
# LionAGI Branch Tutorial

## Introduction

This tutorial introduces the `Branch` class in the LionAGI framework, which facilitates creating and managing conversational branches with various functionalities. This guide will cover creating branches, interacting with the chat interface, retrieving responses, and using external tools through LionAGI's `Branch` class.

## Table of Contents

1. [Setting Up the Branch](#setting-up-the-branch)
2. [Chat Interaction](#chat-interaction)
3. [Working with Tools](#working-with-tools)
4. [Reviewing Metadata](#reviewing-metadata)
5. [Conclusion](#conclusion)

## Setting Up the Branch

To start, you need to import the LionAGI package and create an instance of the `Branch` class.

### Example Usage

The following code demonstrates how to import LionAGI and create a `Branch` instance.

```python
import lionagi as li

# Create a Branch instance
a = li.Branch()
```

## Chat Interaction

Once you have a `Branch` instance, you can interact with the chat interface by inputting a message and awaiting the response.

### Example Usage

The following code demonstrates how to input a chat message and await a response.

```python
# Input a message and await a response
await a.chat("tell me a 10 word story")
# Output: 'A lost cat found its way home after many days wandering.'
```

## Working with Tools

The `Branch` class allows you to define and use external tools for more complex interactions. You can define a tool, such as a calculator function, and invoke it within a chat interaction.

### Example Usage

The following code demonstrates how to define a multiplication tool and use it in a chat interaction.

```python
import lionagi as li

# Define an asynchronous multiplication function
async def multiply(number1: float, number2: float, number3: float = 1):
    """
    Multiply three numbers.

    Args:
        number1: First number to multiply.
        number2: Second number to multiply.
        number3: Third number to multiply.

    Returns:
        The product of number1, number2, and number3.
    """
    return number1 * number2 * number3

# Define an instruction and context for the problem to solve
instruction = """
solve the following problem
"""

context = """
I have 730,000 trees, with an average of 123 apples per tree, each weighing 0.4 lbs.
20 percent are bad and sold for 0.1 dollar per lbs, 30 percent are sold to 
brewery for 0.3 dollar per apple. What is my revenue?
"""

# Create a Branch instance with the multiply tool
branch = li.Branch("act like a calculator, invoke tool uses", tools=[multiply])

# Send the instruction and context, and await the response
await branch.chat(instruction=instruction, context=context, tools=True)
```

## Reviewing Metadata

You can inspect the metadata associated with each message to get additional details about the interaction, such as timestamps and usage statistics.

### Example Usage

The following code demonstrates how to inspect the metadata of messages.

```python
# Convert messages to a DataFrame for inspection
a.messages.to_df()

# Inspect metadata of a specific message
a.messages[1].metadata
```

The metadata provides information about the sender, recipient, timestamps, and additional details relevant to the interaction.

## Conclusion

In this tutorial, we covered the basics of using the `Branch` class from the LionAGI framework, including setting up a branch, interacting with the chat interface, handling responses, working with external tools, and reviewing metadata. By understanding these functionalities, you can effectively manage complex conversational interactions and integrate external tools within your LionAGI-based systems.
