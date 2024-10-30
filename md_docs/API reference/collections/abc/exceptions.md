
### Class: `LionAGIError`

^c6806f

**Parent Class:** [`Exception`](https://docs.python.org/3/library/exceptions.html)

**Description**:
`LionAGIError` is the base class for all exceptions in the LionAGI system.

**Attributes:**
- `message` (str): The error message. Defaults to "An unspecified error occurred in the LionAGI system."

**Usage Examples**:
```python
try:
    raise LionAGIError("Custom error message")
except LionAGIError as e:
    print(e)
```

### Class: `LionValueError`

**Parent Class:** [[#^c6806f|LionAGIError]]


**Description**:
`LionValueError` is an exception raised for errors in the input value.

**Attributes:**
- `message` (str): The error message. Defaults to "An error occurred in the input value."

**Usage Examples**:
```python
try:
    raise LionValueError("Invalid input value")
except LionValueError as e:
    print(e)
```


### Class: `LionTypeError`

^8519bb

**Parent Class:** [[#^c6806f|LionAGIError]]

**Description**:
`LionTypeError` is an exception raised for type mismatch or type checking errors.

**Attributes:**
- `message` (str): The error message. Defaults to "Item must be identifiable, `ln_id` or `Component`."

**Usage Examples**:
```python
try:
    raise LionTypeError("Type mismatch error")
except LionTypeError as e:
    print(e)
```

### Class: `LionItemError`

^767aee

**Parent Class:** [[#^c6806f|LionAGIError]]

**Description**:
`LionItemError` is the base class for exceptions related to LionAGI items.

**Attributes:**
- `message` (str): The error message.  Defaults to "An error occurred with the specified item."
- `item` (Any): The item associated with the error.

**Usage Examples**:
```python
try:
    raise LionItemError("item123", "Custom item error")
except LionItemError as e:
    print(e)
```

### Class: `ItemNotFoundError`

^ee9dbb

**Parent Class:** [[#^767aee|LionItemError]]

**Description**:
`ItemNotFoundError` is an exception raised when a specified item is not found.

**Attributes:**
- `message` (str): The error message.
- `item` (Any): The item associated with the error.

**Usage Examples**:
```python
try:
    raise ItemNotFoundError("item123")
except ItemNotFoundError as e:
    print(e)
```

### Class: `ItemInvalidError`

**Parent Class:** [[#^767aee|LionItemError]]

**Description**:
`ItemInvalidError` is an exception raised when an invalid item is used in an operation.

**Attributes:**
- `message` (str): The error message.
- `item` (Any): The item associated with the error.

**Usage Examples**:
```python
try:
    raise ItemInvalidError("item123")
except ItemInvalidError as e:
    print(e)
```

### Class: `FieldError`

**Parent Class:** [[#^c6806f|LionAGIError]]

**Description**:
`FieldError` is an exception raised for errors in field validation.

**Attributes:**
- `message` (str): The error message. Defaults to "An error occurred with the specified field."
- `field` (str): The field associated with the error.

**Usage Examples**:
```python
try:
    raise FieldError("field_name", "Custom field error")
except FieldError as e:
    print(e)
```

### Class: `LionOperationError`

^0396c9

**Parent Class:** [[#^c6806f|LionAGIError]]

**Description**:
`LionOperationError` is the base class for exceptions related to operational failures.

**Attributes:**
- `message` (str): The error message. Defaults to "An operation failed."
- `operation` (str): The operation associated with the error.

**Usage Examples**:
```python
try:
    raise LionOperationError("operation_name", "Custom operation error")
except LionOperationError as e:
    print(e)
```

### Class: `ConcurrencyError`

**Parent Class:** [[#^0396c9|LionAGIOperationError]]

**Description**:
`ConcurrencyError` is an exception raised for errors due to concurrency issues.

**Attributes:**
- `message` (str): The error message.
- `operation` (str): The operation associated with the error. Defaults to "a concurrent operation".

**Usage Examples**:
```python
try:
    raise ConcurrencyError("operation_name")
except ConcurrencyError as e:
    print(e)
```

### Class: `RelationError`

**Parent Class:** [[#^c6806f|LionAGIError]]

**Description**:
`RelationError` is an exception raised for errors in relation operations.

**Attributes:**
- `message` (str): The error message. Defaults to "Nodes are not related."

**Usage Examples**:
```python
try:
    raise RelationError("Custom relation error")
except RelationError as e:
    print(e)
```

### Class: `ActionError`

**Parent Class:** [[#^c6806f|LionAGIError]]

**Description**:
`ActionError` is an exception raised for errors in action operations.

**Attributes:**
- `message` (str): The error message. Defaults to "An error occurred with the specified action."

**Usage Examples**:
```python
try:
    raise ActionError("Custom action error")
except ActionError as e:
    print(e)
```

### Class: `ModelLimitExceededError`

^f38868

**Parent Class:** [[#^0396c9|LionAGIOperationError]]

**Description**:
`ModelLimitExceededError` is an exception raised when a resource limit is exceeded.

Attributes:
- `message` (str): The error message. Defaults to "The model limit has been exceeded."

**Usage Examples**:
```python
try:
    raise ModelLimitExceededError("Custom limit exceeded message")
except ModelLimitExceededError as e:
    print(e)
```

### Class: `TimeoutError`

**Parent Class:** [[#^0396c9|LionAGIOperationError]]

**Description**:
`TimeoutError` is an exception raised when an operation times out.

Attributes:
- `message` (str): The error message.
- `operation` (str): The operation associated with the error.
- `timeout` (int): The timeout duration in seconds.


**Usage Examples**:
```python
try:
    raise TimeoutError("operation_name", 30)
except TimeoutError as e:
    print(e)
```

### Class: `ServiceError`

**Parent Class:** [[#^c6806f|LionAGIError]]

**Description**:
`ServiceError` is an exception raised for errors in endpoint configuration.

Attributes:
- `message` (str): The error message.
- `errors` (Any): Additional error details.

**Usage Examples**:
```python
try:
    raise ServiceError("Service configuration error")
except ServiceError as e:
    print(e)
```

#### `unavailable`

**Signature**:
```python
@classmethod
def unavailable(cls, endpoint, service, err_msg=None)
```

**Parameters**:
- `endpoint` (str): The endpoint that is unavailable.
- `service` (Any): The service associated with the error.
- `err_msg`

 (str, optional): Additional error message. Defaults to `None`.

**Return Values**:
- `ServiceError`: The constructed `ServiceError` instance.

**Description**:
Constructs a `ServiceError` indicating that an endpoint is currently unavailable.

**Usage Examples**:
```python
try:
    raise ServiceError.unavailable("endpoint_name", service_instance, "Custom error message")
except ServiceError as e:
    print(e)
```
