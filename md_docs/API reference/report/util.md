
### Function: `get_input_output_fields`

**Description**:
Parses an assignment string to extract input and output fields.

**Signature**:
```python
def get_input_output_fields(str_: str) -> list[list[str]]:
```

**Parameters**:
- `str_` (str): The assignment string in the format 'inputs -> outputs'.

**Return Values**:
- `list[list[str]]`: A list containing two lists - one for input fields and one for requested fields.

**Exceptions Raised**:
- `ValueError`: If the assignment string is `None` or if it does not contain '->' indicating an invalid format.

**Usage Examples**:
```python
# Example 1: Parsing a valid assignment string
assignment = "input1, input2 -> output1, output2"
input_fields, requested_fields = get_input_output_fields(assignment)
print(input_fields)  # Output: ['input1', 'input2']
print(requested_fields)  # Output: ['output1', 'output2']

# Example 2: Handling invalid assignment format
try:
    invalid_assignment = "input1, input2 output1, output2"
    get_input_output_fields(invalid_assignment)
except ValueError as e:
    print(e)  # Output: Invalid assignment format. Expected 'inputs -> outputs'.
```
