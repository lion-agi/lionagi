function_field_description = """
Specify the exact name of the function to call from available tool_schemas.

Requirements:
1. Choose only from provided tool_schemas
2. Set to None if no tool_schemas available
3. Do not invent or modify function names

Validation:
- Verify function exists in schema before calling
- Confirm all required parameters are available
- Check function compatibility with current context

Error Handling:
- Report immediately if function not found
- Provide clear error context if validation fails
"""


arguments_field_description = """
Provide function arguments as a schema-compliant dictionary.

Requirements:
1. Use only schema-specified argument names and types
2. Validate all arguments before submission
3. Handle missing or default values explicitly

Validation Steps:
- Type checking for all arguments
- Range/boundary validation where applicable
- Format verification for structured data
- Null/empty value handling

Error Cases:
- Invalid argument types
- Missing required arguments
- Out-of-range values
"""
