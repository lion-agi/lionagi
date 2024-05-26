
### Function: `to_list_type`

**Description**:
`to_list_type` is a utility function that converts various types of input values to a list. It ensures that the input value is converted to a list, handling multiple types such as `Component`, `Mapping`, `Record`, `tuple`, `list`, `set`, `Generator`, and `deque`.

**Signature**:
```python
def to_list_type(value) -> list
```

**Parameters**:
- `value`: The value to convert to a list. It can be of various types including `Component`, `Mapping`, `Record`, `tuple`, `list`, `set`, `Generator`, and `deque`.

**Return Values**:
- `list`: The converted list.

**Exceptions Raised**:
- `TypeError`: Raised if the value cannot be converted to a list.

**Usage Examples**:
```python
# Example 1: Convert a single Component to a list
component = Component()
converted_list = to_list_type(component)
print(converted_list)  # Output: [component]

# Example 2: Convert a tuple to a list
tuple_value = (1, 2, 3)
converted_list = to_list_type(tuple_value)
print(converted_list)  # Output: [1, 2, 3]

# Example 3: Convert a set to a list
set_value = {4, 5, 6}
converted_list = to_list_type(set_value)
print(converted_list)  # Output: [4, 5, 6]

# Example 4: Convert a generator to a list
generator_value = (x for x in range(3))
converted_list = to_list_type(generator_value)
print(converted_list)  # Output: [0, 1, 2]
```

### Function: `_validate_order`

**Description**:
`_validate_order` is a utility function that validates and converts an input value to a list of strings, ensuring that the input value represents a valid order. It handles various input types such as `str`, `Ordering`, and `Element`.

**Signature**:
```python
def _validate_order(value) -> list[str]
```

**Parameters**:
- `value`: The value to validate and convert. It can be of various types including `str`, `Ordering`, and `Element`.

**Return Values**:
- `list[str]`: The validated and converted order list.

**Exceptions Raised**:
- `LionTypeError`: Raised if the value contains invalid types.

**Usage Examples**:
```python
# Example 1: Validate a string value
order_value = "12345678901234567890123456789012"
validated_order = _validate_order(order_value)
print(validated_order)  # Output: ["12345678901234567890123456789012"]

# Example 2: Validate an Ordering object
ordering_value = Ordering()
ordering_value.order = ["12345678901234567890123456789012", "23456789012345678901234567890123"]
validated_order = _validate_order(ordering_value)
print(validated_order)  # Output: ["12345678901234567890123456789012", "23456789012345678901234567890123"]

# Example 3: Validate an Element object
element_value = Element()
element_value.ln_id = "12345678901234567890123456789012"
validated_order = _validate_order(element_value)
print(validated_order)  # Output: ["12345678901234567890123456789012"]

# Example 4: Validate a list of Elements
element_list = [Element(ln_id="12345678901234567890123456789012"), Element(ln_id="23456789012345678901234567890123")]
validated_order = _validate_order(element_list)
print(validated_order)  # Output: ["12345678901234567890123456789012", "23456789012345678901234567890123"]
```
