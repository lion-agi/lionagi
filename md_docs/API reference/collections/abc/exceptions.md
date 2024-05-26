
### Class: `LionAGIError`

**Description**:
`LionAGIError` is the base class for all exceptions in the LionAGI system.

#### Attributes:
- `message` (str): The error message.

### Method: `__init__`

**Signature**:
```python
def __init__(self, message=None)
```

**Parameters**:
- `message` (str, optional): The error message. Defaults to "An unspecified error occurred in the LionAGI system."

**Usage Examples**:
```python
try:
    raise LionAGIError("Custom error message")
except LionAGIError as e:
    print(e)
```

---

### Class: `LionValueError`

**Description**:
`LionValueError` is an exception raised for errors in the input value.

#### Attributes:
- `message` (str): The error message.

### Method: `__init__`

**Signature**:
```python
def __init__(self, message=None)
```

**Parameters**:
- `message` (str, optional): The error message. Defaults to "An error occurred in the input value."

**Usage Examples**:
```python
try:
    raise LionValueError("Invalid input value")
except LionValueError as e:
    print(e)
```

---

### Class: `LionTypeError`

**Description**:
`LionTypeError` is an exception raised for type mismatch or type checking errors.

#### Attributes:
- `message` (str): The error message.

### Method: `__init__`

**Signature**:
```python
def __init__(self, message=None)
```

**Parameters**:
- `message` (str, optional): The error message. Defaults to "Item must be identifiable, `ln_id` or `Component`."

**Usage Examples**:
```python
try:
    raise LionTypeError("Type mismatch error")
except LionTypeError as e:
    print(e)
```

---

### Class: `LionItemError`

**Description**:
`LionItemError` is the base class for exceptions related to LionAGI items.

#### Attributes:
- `message` (str): The error message.
- `item` (Any): The item associated with the error.

### Method: `__init__`

**Signature**:
```python
def __init__(self, item, message=None)
```

**Parameters**:
- `item` (Any): The item associated with the error.
- `message` (str, optional): The error message. Defaults to "An error occurred with the specified item."

**Usage Examples**:
```python
try:
    raise LionItemError("item123", "Custom item error")
except LionItemError as e:
    print(e)
```

---

### Class: `ItemNotFoundError`

**Description**:
`ItemNotFoundError` is an exception raised when a specified item is not found.

#### Attributes:
- `message` (str): The error message.
- `item` (Any): The item associated with the error.

### Method: `__init__`

**Signature**:
```python
def __init__(self, item)
```

**Parameters**:
- `item` (Any): The item associated with the error.

**Usage Examples**:
```python
try:
    raise ItemNotFoundError("item123")
except ItemNotFoundError as e:
    print(e)
```

---

### Class: `ItemInvalidError`

**Description**:
`ItemInvalidError` is an exception raised when an invalid item is used in an operation.

#### Attributes:
- `message` (str): The error message.
- `item` (Any): The item associated with the error.

### Method: `__init__`

**Signature**:
```python
def __init__(self, item)
```

**Parameters**:
- `item` (Any): The item associated with the error.

**Usage Examples**:
```python
try:
    raise ItemInvalidError("item123")
except ItemInvalidError as e:
    print(e)
```

---

### Class: `FieldError`

**Description**:
`FieldError` is an exception raised for errors in field validation.

#### Attributes:
- `message` (str): The error message.
- `field` (str): The field associated with the error.

### Method: `__init__`

**Signature**:
```python
def __init__(self, field, message=None)
```

**Parameters**:
- `field` (str): The field associated with the error.
- `message` (str, optional): The error message. Defaults to "An error occurred with the specified field."

**Usage Examples**:
```python
try:
    raise FieldError("field_name", "Custom field error")
except FieldError as e:
    print(e)
```

---

### Class: `LionOperationError`

**Description**:
`LionOperationError` is the base class for exceptions related to operational failures.

#### Attributes:
- `message` (str): The error message.
- `operation` (str): The operation associated with the error.

### Method: `__init__`

**Signature**:
```python
def __init__(self, operation, message=None)
```

**Parameters**:
- `operation` (str): The operation associated with the error.
- `message` (str, optional): The error message. Defaults to "An operation failed."

**Usage Examples**:
```python
try:
    raise LionOperationError("operation_name", "Custom operation error")
except LionOperationError as e:
    print(e)
```

---

### Class: `ConcurrencyError`

**Description**:
`ConcurrencyError` is an exception raised for errors due to concurrency issues.

#### Attributes:
- `message` (str): The error message.
- `operation` (str): The operation associated with the error.

### Method: `__init__`

**Signature**:
```python
def __init__(self, operation=None)
```

**Parameters**:
- `operation` (str, optional): The operation associated with the error. Defaults to "a concurrent operation".

**Usage Examples**:
```python
try:
    raise ConcurrencyError("operation_name")
except ConcurrencyError as e:
    print(e)
```

---

### Class: `RelationError`

**Description**:
`RelationError` is an exception raised for errors in relation operations.

#### Attributes:
- `message` (str): The error message.

### Method: `__init__`

**Signature**:
```python
def __init__(self, message=None)
```

**Parameters**:
- `message` (str, optional): The error message. Defaults to "Nodes are not related."

**Usage Examples**:
```python
try:
    raise RelationError("Custom relation error")
except RelationError as e:
    print(e)
```

---

### Class: `ActionError`

**Description**:
`ActionError` is an exception raised for errors in action operations.

#### Attributes:
- `message` (str): The error message.

### Method: `__init__`

**Signature**:
```python
def __init__(self, message=None)
```

**Parameters**:
- `message` (str, optional): The error message. Defaults to "An error occurred with the specified action."

**Usage Examples**:
```python
try:
    raise ActionError("Custom action error")
except ActionError as e:
    print(e)
```

---

### Class: `ModelLimitExceededError`

**Description**:
`ModelLimitExceededError` is an exception raised when a resource limit is exceeded.

#### Attributes:
- `message` (str): The error message.

### Method: `__init__`

**Signature**:
```python
def __init__(self, message=None)
```

**Parameters**:
- `message` (str, optional): The error message. Defaults to "The model limit has been exceeded."

**Usage Examples**:
```python
try:
    raise ModelLimitExceededError("Custom limit exceeded message")
except ModelLimitExceededError as e:
    print(e)
```

---

### Class: `TimeoutError`

**Description**:
`TimeoutError` is an exception raised when an operation times out.

#### Attributes:
- `message` (str): The error message.
- `operation` (str): The operation associated with the error.
- `timeout` (int): The timeout duration in seconds.

### Method: `__init__`

**Signature**:
```python
def __init__(self, operation, timeout)
```

**Parameters**:
- `operation` (str): The operation associated with the error.
- `timeout` (int): The timeout duration in seconds.

**Usage Examples**:
```python
try:
    raise TimeoutError("operation_name", 30)
except TimeoutError as e:
    print(e)
```

---

### Class: `ServiceError`

**Description**:
`ServiceError` is an exception raised for errors in endpoint configuration.

#### Attributes:
- `message` (str): The error message.
- `errors` (Any): Additional error details.

### Method: `__init__`

**Signature**:
```python
def __init__(self, message, errors=None)
```

**Parameters**:
- `message` (str): The error message.
- `errors` (Any, optional): Additional error details.

**Usage Examples**:
```python
try:
    raise ServiceError("Service configuration error")
except ServiceError as e:
    print(e)
```

### Method: `unavailable`

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
