
### Class: `BaseForm`

**Parent Class:** [[Component#^ce462d|Component]]

^f8937b

**Description**:
`BaseForm` is a base class for handling form-like structures within an application. It manages form components and operations such as filling forms and checking their state (filled, workable).

#### Attributes:
- `template_name` (str): The name of the template used by the form.
- `assignment` (str | None): The objective of the form specifying input/output fields.
- `input_fields` (List[str]): Fields required to carry out the objective of the form.
- `requested_fields` (List[str]): Fields requested to be filled by the user.
- `task` (Any): The work to be done by the form, including custom instructions.
- `validation_kwargs` (Dict[str, Dict[str, Any]]): Additional validation constraints for the form fields.

### `work_fields`

**Signature**:
```python
@property
def work_fields(self) -> Dict[str, Any]:
```

**Return Values**:
- `Dict[str, Any]`: The fields relevant to the current task.

**Description**:
Get the fields relevant to the current task. Must be implemented by subclasses.

### `fill`

**Signature**:
```python
def fill(self, *args, **kwargs):
```

**Parameters**:
- `*args`: Additional positional arguments.
- `**kwargs`: Additional keyword arguments.

**Description**:
Fill the form from various sources, including other forms and additional fields. Implement this method in subclasses.

### `is_workable`

**Signature**:
```python
def is_workable(self) -> bool:
```

**Return Values**:
- `bool`: True if the form is workable, otherwise False.

**Description**:
Check if the form object is ready for work execution. Raise an error if the form is not workable. Use with the workable property.

### `filled`

**Signature**:
```python
@property
def filled(self) -> bool:
```

**Return Values**:
- `bool`: True if the form is filled, otherwise False.

**Description**:
Check if the form is filled with all required fields. Uses the _is_filled method and suppresses any `ValueError` raised by it.

### `workable`

**Signature**:
```python
@property
def workable(self) -> bool:
```

**Return Values**:
- `bool`: True if the form is workable, otherwise False.

**Description**:
Check if the form is workable. This property does not raise an error and will return True or False.

### `_is_filled`

**Signature**:
```python
def _is_filled(self) -> bool:
```

**Return Values**:
- `bool`: True if all work fields are filled, otherwise raises `ValueError`.

**Exceptions Raised**:
- `ValueError`: If any field is not filled.

**Description**:
Private method to check if all work fields are filled. Raises a `ValueError` if any field is not filled.

### `_get_all_fields`

**Signature**:
```python
def _get_all_fields(
    self, form: List["BaseForm"] = None, **kwargs
) -> Dict[str, Any]:
```

**Parameters**:
- `form` (List[BaseForm], optional): A list of forms to gather fields from.
- `**kwargs`: Additional fields to include.

**Return Values**:
- `Dict[str, Any]`: A dictionary of all gathered fields.

**Description**:
Given a form or collections of forms, and additional fields, gather all fields together including self fields with valid value.

### `copy`

**Signature**:
```python
def copy(self)
```

**Return Values**:
- `BaseForm`: A copy of the current form.

**Description**:
Creates a copy of the form.

**Usage Examples**:
```python
class MyForm(BaseForm):
    @property
    def work_fields(self) -> Dict[str, Any]:
        return {
            "field1": self.field1,
            "field2": self.field2,
        }

    def fill(self, *args, **kwargs):
        self.field1 = kwargs.get("field1", self.field1)
        self.field2 = kwargs.get("field2", self.field2)

    def is_workable(self) -> bool:
        return bool(self.field1 and self.field2)

my_form = MyForm()
my_form.fill(field1="value1", field2="value2")
print(my_form.filled)  # Output: True
print(my_form.workable)  # Output: True
copy_form = my_form.copy()
print(copy_form.filled)  # Output: True
```
