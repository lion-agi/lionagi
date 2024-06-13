
# LionAGI Direct Interaction with Tools Tutorial

## Introduction

In this tutorial, we will explore how to use the `Branch.direct` method in LionAGI with the addition of tools. This approach allows for structured interactions where the AI can call functions (tools) to perform specific tasks as part of its reasoning process.

## Table of Contents

1. [Setup](#setup)
2. [Defining Helper Functions](#defining-helper-functions)
3. [Context Definition](#context-definition)
4. [Creating and Registering Tools](#creating-and-registering-tools)
5. [Using Branch.direct with Tools](#using-branchdirect-with-tools)
6. [Conclusion](#conclusion)

## Setup

First, let's import the necessary libraries and initialize the LionAGI module.

```python
import lionagi as li
```

## Defining Helper Functions

Define a helper function to nicely print form fields.

```python
from IPython.display import display, Markdown

def nice_print(form):
    for k, v in form.work_fields.items():
        display(Markdown(f"{k}: \n{v}\n"))
```

## Context Definition

Define the context for our example, including two basic math questions.

```python
question1 = "A school is ordering laptops for its students. If each classroom has 25 students and the school wants to provide a laptop for each student in its 8 classrooms, how many laptops in total does the school need to order?"
question2 = "A bakery sells cupcakes in boxes of 6. If a customer wants to buy 8 boxes, with each person getting one cupcake, how many people can the customer serve cupcake to?"

import json

context = {"Question1": question1, "question2": question2}
context = json.dumps(context)
```

## Creating and Registering Tools

Define a function that performs multiplication and convert it into a tool.

```python
from lionagi.core.action import func_to_tool

def multiply(number1: float, number2: float):
    """
    Perform multiplication on two numbers.
    such as 2, 3.5, etc.

    Args:
        number1: First number to multiply.
        number2: Second number to multiply.

    Returns:
        The product of number1 and number2.
    """
    return number1 * number2

tool_m = func_to_tool(multiply)
```

Register the tool with the branch.

```python
branch = li.Branch()
branch.register_tools(multiply)
```

## Using Branch.direct with Tools

Use the `Branch.direct` method to perform structured reasoning and call the registered tool to solve the math questions.

```python
out_ = await branch.direct(
    instruction="Think step by step, understand the following basic math question and provide parameters for function calling.",
    context=context,
    tools=tool_m,
    reason=True,
    score=True,
    allow_action=True,
)
```

Display the structured output.

```python
nice_print(out_)
```

Expected Output:

```markdown
task: 
Follow the prompt and provide the necessary output.
- Additional instruction: Think step by step, understand the following basic math question and provide parameters for function calling.
- Additional context: {"Question1": "A school is ordering laptops for its students. If each classroom has 25 students and the school wants to provide a laptop for each student in its 8 classrooms, how many laptops in total does the school need to order?", "question2": "A bakery sells cupcakes in boxes of 6. If a customer wants to buy 8 boxes, with each person getting one cupcake, how many people can the customer serve cupcake to?"}
- Perform reasoning and prepare actions with GIVEN TOOLS ONLY.
- Perform scoring according to score range: [0, 10] and precision: integer.

reason: 
Let's think step by step, because we need to perform multiplication to find the answers to both questions.

actions: 
{'action_1': {'function': 'functions.multiply', 'arguments': {'number1': 25, 'number2': 8}}, 'action_2': {'function': 'functions.multiply', 'arguments': {'number1': 6, 'number2': 8}}}

action_required: 
True

answer: 
The school needs to order 200 laptops. The customer can serve cupcakes to 48 people.

score: 
10

action_response: 
{'action_1': {'function': 'multiply', 'arguments': {'number1': 25, 'number2': 8}, 'output': 200}, 'action_2': {'function': 'multiply', 'arguments': {'number1': 6, 'number2': 8}, 'output': 48}}

action_performed: 
True
```

## Conclusion

In this tutorial, we explored how to use the `Branch.direct` method in LionAGI with the addition of tools. This approach allows for more structured interactions, where the AI can perform specific tasks using registered functions. Understanding how to combine `Branch.direct` with tools can help in solving complex problems more effectively by leveraging the AI's reasoning capabilities along with function calls.
