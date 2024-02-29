
Leveraging LionAGI's `func_to_tool` function streamlines the process of integrating custom logic into conversational flows by automatically generating a tool schema from a function. This powerful feature simplifies the creation of `Tool` objects, making it easier to utilize custom functions within a `Session` object.

### Automatic Schema Generation with `func_to_tool`

The `func_to_tool` utility in LionAGI automatically generates a schema for your functions based on type hints and docstrings. This approach enables you to focus on the logic of your functions without worrying about manually crafting schemas.

#### How to Use `func_to_tool`

1. **Define Your Function**: Write your function with clear type hints and a descriptive docstring. The quality of the automatically generated schema heavily relies on the detail provided in the docstring.

2. **Generate the Tool Object**: Use `func_to_tool` to convert your function into a `Tool` object, complete with an inferred schema.

#### Example: Creating a Tool with `func_to_tool`

```python
import lionagi.core.action.tool_manager
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


# Automatically generate a Tool object
tool_add = lionagi.core.action.tool_manager.func_to_tool(add_numbers)

# Inspect the generated schema
print(li.to_readable_dict(tool_add.schema_))
```

This method supports both Google and reStructuredText (reST) docstring formats, allowing you to use the style that best fits your project.

### Registering Tools in a Session

Once you have created your `Tool` objects, you can register them within a session to make them available for function calling. This step is crucial for informing the session which custom functions can be utilized during conversations.

#### Registering Multiple Tools

You can register one or more tools with a session using the `register_tools` method. This method accepts a list of `Tool` objects or schemas, making it flexible for different use cases.

```python
# Initialize a session with a system message
session = li.Session(system="Function picker and parameter provider")

# Register the previously created add tool
session.register_tools([tool_add])

# Optionally, update session configurations
session.default_branch.llmconfig.update({
    "temperature": 0.35,
    "tool_choice": "auto", 
    "response_format": {'type': 'json_object'}
})
```

### Specifying Tools for Function Calls

When making a function call within a session, you can specify which tool(s) to use. This specification can be a single tool, a subset of registered tools, or all tools by setting `tools=True`.

```python
response = await session.chat(
    instruction="Calculate the sum of two numbers.",
    context={"number1": 5, "number2": 3},
    tools='add_numbers',  # Specify the tool by its name
    response_format={'type': 'json_object'}
)
```

### Conclusion

LionAGI's `func_to_tool` function significantly eases the process of creating and utilizing custom tools within sessions, enhancing the AI's ability to perform specialized tasks based on conversational context. By automatically generating tool schemas from well-documented functions, LionAGI empowers developers to seamlessly integrate complex logic into their conversational applications, opening up a wide range of possibilities for interactive and dynamic AI-driven solutions.