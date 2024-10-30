
### Class: `Package`

**Parent Class: [[Component#^bb802e|Element]]

**Description**:
`Package` represents a package to be delivered, categorized by its type. It includes the source of the request, the category of the package, and the package content itself.

#### Attributes:
- `request_source` (str | None): The source of the request. Default is `None`.
- `category` (PackageCategory): The category of the package.
- `package` (Any): The package content to be delivered.

### `validate_category`

**Signature**:
```python
@field_validator("category", mode="before")
def validate_category(cls, value: Any)
```

**Parameters**:
- `value` (Any): The value to validate as a `PackageCategory`.

**Return Values**:
- `PackageCategory`: The validated category value.

**Exceptions Raised**:
- `ValueError`: If the category value is `None` or invalid.

**Description**:
Validates the `category` field to ensure it is a valid `PackageCategory`. If the value is not already a `PackageCategory`, it attempts to convert it. Raises a `ValueError` if the value is `None` or cannot be converted.

**Usage Examples**:
```python
package = Package(category="message", package="This is a test package")
print(package.category)  # Output: PackageCategory.MESSAGE

# Example of invalid category
try:
    package = Package(category="invalid_category", package="This will raise an error")
except ValueError as e:
    print(e)  # Output: Invalid value for category: invalid_category.
```

### Enum: `PackageCategory`

**Description**:
`PackageCategory` is an enumeration representing different categories of packages. The categories include MESSAGE, TOOL, IMODEL, NODE, NODE_LIST, NODE_ID, START, END, and CONDITION.

**Values**:
- `MESSAGE = "message"`
- `TOOL = "tool"`
- `IMODEL = "imodel"`
- `NODE = "node"`
- `NODE_LIST = "node_list"`
- `NODE_ID = "node_id"`
- `START = "start"`
- `END = "end"`
- `CONDITION = "condition"`

**Usage Examples**:
```python
print(PackageCategory.MESSAGE)  # Output: PackageCategory.MESSAGE
print(PackageCategory.MESSAGE.value)  # Output: "message"
```
