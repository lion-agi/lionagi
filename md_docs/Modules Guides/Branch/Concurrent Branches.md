To harness the full capabilities of LionAGI's `func_to_tool` for generating `Tool` objects, it's essential to provide detailed Google-style docstrings for your functions. These docstrings play a crucial role in automatically inferring the schema of the tool, including parameter types and descriptions. Let's refine our approach to creating concurrent branches with custom tools by ensuring our functions are well-documented with Google-style docstrings.

### Defining Functions with Google-style Docstrings

Google-style docstrings include a description of the function, its arguments, return types, and any other relevant information. This detailed documentation enables `func_to_tool` to accurately generate a tool schema.

**Example: Defining Functions with Docstrings**

```python
import lionagi as li

# Define the multiply function with a Google-style docstring
def multiply(number1: float, number2: float) -> float:
    """
    Perform multiplication on two numbers.

    Args:
        number1 (float): The first number to multiply.
        number2 (float): The second number to multiply.

    Returns:
        float: The product of number1 and number2.
    """
    return number1 * number2

# Define the add function with a Google-style docstring
def add(number1: float, number2: float) -> float:
    """
    Add up two numbers.

    Args:
        number1 (float): The first number to add.
        number2 (float): The second number to add.

    Returns:
        float: The sum of number1 and number2.
    """
    return number1 + number2
```

**Generating Tool Objects with `func_to_tool`**

With the functions defined, use `func_to_tool` to generate `Tool` objects, which will include the automatically inferred schema based on the provided docstrings.

```python
# Automatically generate Tool objects
tool_mul = li.func_to_tool(multiply)
tool_add = li.func_to_tool(add)
```

### Setting Up Concurrent Branches

Create branches for each specific task, like `calc_mul` for multiplication and `calc_add` for addition, and register the corresponding tools to these branches.

```python
# Initialize a session
session = li.Session()

# Create branches for different calculations
session.new_branch('calc_mul')
session.new_branch('calc_add')

# Register tools to the respective branches
session.branches['calc_mul'].register_tools(tool_mul)
session.branches['calc_add'].register_tools(tool_add)
```

### Branch Info Exchange and Concurrent Processing

LionAGI's branch system allows for the exchange of messages, tools, services, or `llmconfig` settings between branches, facilitating complex workflows where branches can interact and share information.

**Example: Exchanging Information Between Branches**

1. **Sending Requests Between Branches**: Utilize the `send` method to request sending of messages or tools between branches.
2. **Collecting and Sending Requests**: The `collect` and `send` methods gather and dispatch requests across branches.
3. **Receiving Requests**: Branches decide which requests to accept through the `receive` method, based on the sender and request type.

```python
# Step-by-step process for exchanging information
session.collect()
session.send()

# Branch 'calc_mul' receives from 'calc_add' and vice versa
session.branches['calc_mul'].receive('calc_add')
session.branches['calc_add'].receive('calc_mul')
```

This advanced branch functionality in LionAGI enables the development of sophisticated AI-driven applications where separate conversational or computational threads can proceed in parallel, interact, and dynamically influence each other, opening new avenues for complex, multi-faceted AI interactions.