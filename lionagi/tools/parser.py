import inspect
import functools

def openai_tool_schema_decorator(required_params=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        function_name = func.__name__
        function_description = func.__doc__ or "No description provided."

        params = inspect.signature(func).parameters
        parameters = {}
        for name, param in params.items():
            if name == 'self':
                continue
            parameters[name] = {
                "type": "string",  # Simplified for the example
                "description": f"Parameter {name}"
            }

        tool_schema = {
            "type": "function",
            "function": {
                "name": function_name,
                "description": function_description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required_params or list(parameters.keys())
                },
            }
        }

        wrapper.tool_schema = tool_schema
        return wrapper
    return decorator

@openai_tool_schema_decorator(required_params=["str_or_query_bundle"])
def query_lionagi_codebase(str_or_query_bundle, optional_param="default"):
    """
    Perform a query to a QA bot with access to a vector index 
    built with package lionagi codebase.
    """
    return f"Querying with: {str_or_query_bundle}"

# Accessing the generated schema
print(query_lionagi_codebase.tool_schema)

{
    "type": "function",
    "function": {
        "name": "query_lionagi_codebase",
        "description": "Perform a query to a QA bot with access to a vector index built with package lionagi codebase.",
        "parameters": {
            "type": "object",
            "properties": {
                "str_or_query_bundle": {
                    "type": "string",
                    "description": "Parameter str_or_query_bundle"
                },
                "optional_param": {
                    "type": "string",
                    "description": "Parameter optional_param"
                }
            },
            "required": ["str_or_query_bundle"]
        }
    }
}
