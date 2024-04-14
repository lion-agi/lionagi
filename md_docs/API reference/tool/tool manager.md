## ToolManager Class

Manages the registration and invocation of tools within the system, handling both synchronous and asynchronous operations.

### Attributes
- `registry (dict[str, Tool])`: Holds registered tools, keyed by their names.

### Methods
- `name_existed(name)`: Checks if a tool name is already registered in the system.
- `has_tools`: Property that checks if there are any tools registered.
- `_register_tool(tool)`: Registers a tool in the registry.
- `invoke(func_calls)`: Invokes a registered tool's function based on the provided name and arguments.
- `get_function_call(response)`: Extracts function call details from a response dictionary.
- `register_tools(tools)`: Registers multiple tools in the registry.
- `to_tool_schema_list()`: Generates a list of schemas for all registered tools.
- `parse_tool(tools, **kwargs)`: Parses tool information and generates a dictionary for tool invocation.

## func_to_tool Function

Transforms callable functions into `Tool` objects by parsing their docstrings to extract metadata and parameters.

### Parameters
- `func_ (Callable | list[Callable])`: The function(s) to be transformed.
- `parser (Optional[Any])`: An optional parser to associate with the resulting Tool.
- `docstring_style (str)`: Indicates the `docstring` style to parse ('google' or 'reST').

### Returns
- `Tool`: A Tool object representing the function, equipped with a schema derived from its `docstring`.

### Description
This function is used to transform regular functions into Tool objects that conform to structured metadata requirements, facilitating their integration into systems that require such detailed metadata for automation or interface generation.

### Note
The accuracy and completeness of the function's `docstring` are crucial for generating a valid Tool schema. Incorrectly formatted docstrings may lead to incomplete or inaccurate schemas.
