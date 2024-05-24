
### Class: `Mail`

**Description**:
`Mail` represents a mail component with sender and recipient information. It extends the `Element` and `Sendable` classes, providing functionalities to handle mail packages within a system.

#### Attributes:
- `package` (Package | None): The package to be delivered.

### Method: `category`

**Signature**:
```python
@property
def category() -> PackageCategory:
```

**Return Values**:
- `PackageCategory`: The category of the package.

**Description**:
Returns the category of the package associated with the mail.

**Usage Examples**:
```python
mail = Mail(...)
category = mail.category
print(category)
```

### Method: `to_dict`

**Signature**:
```python
def to_dict() -> dict:
```

**Return Values**:
- `dict`: A dictionary representation of the mail.

**Description**:
Converts the mail object to a dictionary format, including the mail's ID, creation timestamp, package category, and package ID.

**Usage Examples**:
```python
mail = Mail(...)
mail_dict = mail.to_dict()
print(mail_dict)
```
