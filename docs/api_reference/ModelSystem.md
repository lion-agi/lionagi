# Model System API Reference

## Overview

The Model system provides structured data handling through four complementary components:
- FieldModel: Defines individual fields with validation and documentation
- ModelParams: Creates Pydantic models dynamically with field configurations
- OperableModel: Enables runtime field modification of model instances
- Note: Manages deeply nested data with dictionary-like access

## Core Components

### FieldModel
Field definition system for type safety and validation.

```python
class FieldModel(SchemaModel):
    """Field definition with validation."""
    
    # Core attributes
    name: str                     # Field identifier
    annotation: type | Any        # Type information
    default: Any = UNDEFINED      # Static default value
    default_factory: Callable     # Dynamic default generator
    
    # Validation
    validator: Callable           # Validation function
    validator_kwargs: dict        # Validator configuration
    
    # Documentation
    title: str | None            # Display name
    description: str | None      # Field documentation
    examples: list | None        # Example values
    
    @property
    def field_info(self) -> FieldInfo:
        """Get Pydantic field configuration."""

# Usage: Define field with validation
email_field = FieldModel(
    name="email",
    annotation=str,
    description="User email address",
    validator=lambda v: v if "@" in v else None
)
```

### ModelParams
Dynamic model creation with field configuration.

```python
class ModelParams(SchemaModel):
    """Model creation configuration."""
    
    # Structure
    name: str | None               # Model class name
    base_type: type[BaseModel]     # Parent model class
    
    # Fields
    parameter_fields: dict[str, FieldInfo]  # Direct field definitions
    field_models: list[FieldModel]         # Field model configurations
    exclude_fields: list                   # Fields to skip
    
    def create_new_model(self) -> type[BaseModel]:
        """Generate model class from configuration."""

# Usage: Create model with fields
user_model = ModelParams(
    name="UserProfile",
    field_models=[
        FieldModel(name="name", annotation=str),
        FieldModel(name="age", annotation=int, default=0)
    ]
).create_new_model()
```

### OperableModel
Runtime field management in model instances.

```python
class OperableModel(HashableModel):
    """Dynamic field operations."""
    
    def add_field(
        self,
        field_name: str,
        value: Any = UNDEFINED,
        annotation: type = UNDEFINED,
        field_model: FieldModel = UNDEFINED,
        **kwargs
    ) -> None:
        """Add new field to instance."""
        
    def update_field(
        self,
        field_name: str,
        value: Any = UNDEFINED,
        **kwargs
    ) -> None:
        """Modify existing field."""

# Usage: Modify fields at runtime
class UserModel(OperableModel):
    name: str

user = UserModel(name="John")
user.add_field("email", annotation=str)
user.update_field("email", value="john@example.com")
```

### Note
Nested data structure with deep access patterns.

```python
class Note(BaseModel):
    """Nested dictionary operations."""
    
    content: dict[str, Any]  # Nested data
    
    def get(
        self,
        indices: str | list[str | int],  # Path to value
        default: Any = UNDEFINED         # Default if missing
    ) -> Any:
        """Retrieve nested value by path."""
        
    def set(
        self,
        indices: str | list[str | int],  # Path to set
        value: Any                       # Value to insert
    ) -> None:
        """Set nested value by path."""
        
    def update(
        self,
        indices: str | list[str | int],  # Path to update
        value: Any                       # Update value/dict
    ) -> None:
        """Update nested structure."""

# Usage: Deep data access
settings = Note(
    user={
        "preferences": {
            "theme": "dark",
            "notifications": True
        }
    }
)

# Access: user.preferences.theme
theme = settings.get(["user", "preferences", "theme"])

# Update: user.preferences
settings.update(["user", "preferences"], {
    "theme": "light",
    "language": "en"
})
```

## Common Patterns

### Field Validation
```python
# Create field with validation
age_field = FieldModel(
    name="age",
    annotation=int,
    validator=lambda v: v if 0 <= v <= 120 else None,
    validator_kwargs={"mode": "before"}
)

# Use in model
params = ModelParams(
    name="UserModel",
    field_models=[age_field]
)
UserModel = params.create_new_model()
```

### Dynamic Fields
```python
class DynamicForm(OperableModel):
    title: str

# Add fields as needed
form = DynamicForm(title="Survey")
form.add_field("question_1", annotation=str)
form.add_field("response_1", annotation=str)

# Update values
form.update_field("response_1", value="Yes")
```

### Nested Operations
```python
# Complex data
profile = Note(
    user={
        "settings": {"theme": "dark"},
        "data": [{"key": "value"}]
    }
)

# Different access patterns
theme = profile.get(["user", "settings", "theme"])  # Path list
value = profile.get(["user", "data", 0, "key"])    # With index
profile.update(["user", "settings"], {"theme": "light"})  # Deep update
