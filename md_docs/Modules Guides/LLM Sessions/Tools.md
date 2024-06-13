

```python
import lionagi as li

# Define a function with type hints and a docstring
def add_numbers(number1: float, number2: float) -> float:
    """
    Adds two numbers and returns the result.

    Args:
        number1 (float): The first number to add.
        number2 (float): The second number to add.

    Returns:
        float: The sum of number1 and number2.
    """
    return number1 + number2
```

This method supports both Google and reStructuredText (reST) docstring formats, allowing you to use the style that best fits your project.

### Registering Tools in a Session

Once you have created your `Tool` objects, you can register them within a session to make them available for function calling. This step is crucial for informing the session which custom functions can be utilized during conversations.

#### Registering Multiple Tools

You can register one or more tools with a session using the `register_tools` method. This method accepts a list of `Tool` objects or schemas, making it flexible for different use cases.

```python
# Initialize a session with a system message
session = li.Session(
	"Function picker and parameter provider", 
	tools=add_numbers  # directly use the functions as tool
)

# Specify the tool by its name
response = await session.chat(
	"Calculate the sum of two numbers.", 
	context = {"number1": 5, "number2": 3}, 
	tools = 'add_numbers'
)
```


### Ways of Specifying Tools

In the following steps, you can specify which tool or set of tools you
want to use in that step.

If you want to specify a single tool to be used in this step, you can
pass in:

-   the name of the tool (str)
-   the `Tool` object
-   a tool schema

If you want to specify a subset of tools, you can pass in a list
containing any of these three types.

By default, no tools will be used. If you want to include all registered
tools in the step, you can add `tools=True`.

``` python
# a tool object can be created by 
from lionagi import func_to_tool

tool_add = func_to_tool(add_numbers)
tool_schema = tool.schema_

# all compatible inputs

# default: no tools will be used
await session.chat(instruction=instruct)

# auto use all registered tools
await session.chat(instruction=instruct, tools=True)

# name
await session.chat(instruction=instruct, tools='add_numbers')

# list of name
await session.chat(instruction=instruct, tools=['add_numbers'])

# tool
await session.chat(instruction=instruct, tools=tool_add)

# list of tool
await session.chat(instruction=instruct, tools=[tool_add])

# schema
await session.chat(instruction=instruct, tools=tool_schema)

# list of schema
await session.chat(instruction=instruct, tools=[tool_schema])
```
