# Operative API Reference

## Overview

Operative manages request and response models for operations, providing validation and model handling capabilities.

## Core Class

```python
class Operative(SchemaModel):
    """Operation handler with request/response model management."""
    
    # Core fields
    name: str | None = None
    
    # Request handling
    request_params: ModelParams | None = Field(
        default=None,
        description="Parameters for request model creation"
    )
    request_type: type[BaseModel] | None = Field(
        default=None,
        description="Generated request model type"
    )
    
    # Response handling
    response_params: ModelParams | None = Field(
        default=None,
        description="Parameters for response model creation"
    )
    response_type: type[BaseModel] | None = Field(
        default=None,
        description="Generated response model type"
    )
    response_model: BaseModel | None = Field(
        default=None,
        description="Active response model instance"
    )
    response_str_dict: dict | str | None = Field(
        default=None,
        description="Raw response data before validation"
    )
    
    # Validation settings
    auto_retry_parse: bool = True    # Enable validation retries
    max_retries: int = 3            # Maximum validation attempts
    parse_kwargs: dict | None = None  # Custom parsing options
```

## Key Methods

### Response Validation

```python
def raise_validate_pydantic(self, text: str) -> None:
    """Strict validation with exceptions.
    
    Validates text against request type schema, raising errors on failure.
    """

def force_validate_pydantic(self, text: str) -> None:
    """Flexible validation without exceptions.
    
    Attempts to match fields and validate, falling back to best effort.
    """

# Usage
try:
    # Try strict validation first
    operative.raise_validate_pydantic(response_text)
except Exception:
    # Fall back to flexible validation
    operative.force_validate_pydantic(response_text)
```

### Response Management

```python
def update_response_model(
    self,
    text: str | None = None,
    data: dict | None = None
) -> BaseModel | dict | str | None:
    """Update response model from text or data.
    
    Updates with validation:
    1. Validates text if provided
    2. Updates model with data if provided
    3. Handles list responses if needed
    """

def create_response_type(
    self,
    response_params: ModelParams | None = None,
    field_models: list[FieldModel] | None = None,
    parameter_fields: dict[str, FieldInfo] | None = None,
    exclude_fields: list[str] | None = None,
    field_descriptions: dict[str, str] | None = None,
    inherit_base: bool = True,
    config_dict: dict | None = None,
    doc: str | None = None,
    frozen: bool = False,
    validators: dict | None = None,
) -> None:
    """Create new response type with parameters."""

# Usage example
operative.create_response_type(
    field_models=[
        FieldModel(name="score", annotation=float),
        FieldModel(name="confidence", annotation=float)
    ],
    inherit_base=True,
    doc="Response with metrics"
)

result = operative.update_response_model(
    text='{"score": 0.92, "confidence": 0.87}'
)
```

## Common Patterns

### Validation Flow

```python
# Initialize operative
operative = Operative(
    name="metrics_analyzer",
    request_params=ModelParams(
        field_models=[
            FieldModel(name="metrics", annotation=dict),
            FieldModel(name="threshold", annotation=float)
        ]
    )
)

# Process response with validation retry
try:
    # Try strict validation
    operative.raise_validate_pydantic(response_text)
except Exception:
    # Try flexible validation
    if operative.auto_retry_parse:
        for _ in range(operative.max_retries):
            try:
                operative.force_validate_pydantic(response_text)
                break
            except Exception:
                continue
```

### Response Type Creation

```python
# Create response type for metrics
operative.create_response_type(
    field_models=[
        FieldModel(
            name="success_rate",
            annotation=float,
            validator=lambda x: 0 <= x <= 1
        ),
        FieldModel(
            name="error_count",
            annotation=int,
            default=0
        )
    ],
    inherit_base=True,
    doc="Metrics analysis results"
)

# Update with results
operative.update_response_model(
    data={"success_rate": 0.95, "error_count": 2}
)
```
