
# Enhancing LLM Capabilities with ReAct and Lionagi

## Overview

The [[react]] method is a transformative approach that enables Large Language Models (LLMs) to tackle complex, multi-step tasks requiring detailed planning and execution. This tutorial illustrates how, with simple computational tools, LLMs can navigate through intricate problems, showcasing their potential beyond text processing.

## The Essence of Simplified Tools

At the core of ReAct's methodology is the integration of elementary operations as tools for the LLM to utilize. These operations, though basic, are pivotal in solving sophisticated challenges when applied strategically.

```python
# Basic operations will be defined here: addition, subtraction, multiplication, division

async def multiply(number1:float, number2:float):
    '''
    multiply two numbers.

    Args:
        number1: First number to multiply.
        number2: Second number to multiply.
    
    Returns:
        The product of number1, number2

    '''
    return number1*number2

tool_multiply = li.func_to_tool(multiply)


async def add(number1:float, number2:float):
    '''
    add two numbers.


    Args:
        number1: First number to add.
        number2: Second number to add.
    
    Returns:
        The sum of number1, number2
    '''
    return number1+number2


async def minus(number1:float, number2:float):
    '''
    number 1 subtract number 2. i.e. a-b

    Args:
        number1: First number
        number2: Second number
    
    Returns:
        number 1 minus number 2.

    '''
    return number1-number2

async def division(number1:float, number2:float):
    '''
    number 1 divide by number 2. i.e. a/b

    Args:
        number1: First number
        number2: Second number
    
    Returns:
        number 1 divide number 2.

    '''
    return number1/number2
```

## Strategic Reasoning with ReAct

ReAct elevates LLMs to the realm of strategic planners. It prompts the LLM to reason about the appropriate tool for each task, guiding it through a sequence of actions towards the solution. 

**Define context**

```plain text
I have 730_000 trees, with average 123 apples per tree, each weigh 0.4 lbs. 20 percent are bad and sold for 0.1 dollar per lbs, 30 percent are sold to brewery for 0.3 dollar per apple, the remaining are sold as fruit for 60 cents per apple. The variable cost of producing apples is 10 cents each apple. The fixed cost is 10 million dollars. 50 million dollars was borrowed from bank, and I repaid in full to bank with 10 percent extra in interest. I have to pay 10 percent of all proceeds as sales tax. And, I need to pay 35 percent on the remaining as business income tax. what is my accounting profit, and what is my cash flow?
```

```python
system = 'Think step by step, perform as a helpful math teacher'
instruction = 'solve the following accounting problem'
context = 'I have...' #copy from above
```

**Set up session**

```python
from lionagi import Session

session = Session(system, tools=[multiply, add, minus, division]) 
```

**Run ReAct Workflow**

```python
result = await session.ReAct(instruction, context=context)
```


## Practical Applications

While our example centers on solving a mathematical problem, the ReAct method's applications are wide-ranging. It's applicable in scenarios that demand sequential decision-making and problem-solving, from programming tasks to data analysis, and beyond.

