---
type: api-reference
title: "LionAGI Step API Reference"
created: 2025-01-05 03:41 EST
updated: 2025-01-05 03:41 EST
status: active
tags: [api-reference, lionagi, operative, step]
aliases: ["Step API"]
sources: 
  - "Local: /users/lion/lionagi/lionagi/operatives/step.py"
confidence: certain
---

# Step API Reference

## Overview

The Step module provides functionality for breaking down operations into manageable steps with reasoning and actions. It consists of two main components:

1. [[Reason API Reference|Reason]]-enabled [[Action Request Message|action requests]] through the StepModel class
2. Utility methods for creating and managing [[Operative API Reference|Operative]] instances through the Step class

Key features:
- Operation breakdown via StepModel
- [[Operative API Reference|Operative]] creation and management
- [[Reason API Reference|Reasoning]] integration
- [[Action Request Message|Action]] handling

## Core Components

### StepModel Class

```python
class StepModel(BaseModel):
    """Model for operation steps with reasoning and actions.
    
    Represents a single step in an operation, optionally including
    reasoning about decisions and required actions to perform.
    
    Used by Step class to create and manage Operative instances.
    """
    
    # Core identification
    title: str  # Step identifier
    description: str  # Step details
    
    # Reasoning and actions
    reason: Reason | None = Field(
        **REASON_FIELD.to_dict(),
        description="Optional reasoning about decisions"
    )
    action_requests: list[ActionRequestModel] = Field(
        **ACTION_REQUESTS_FIELD.to_dict(),
        description="Actions to perform in this step"
    )
    action_required: bool = Field(
        **ACTION_REQUIRED_FIELD.to_dict(),
        description="Whether actions must be executed"
    )
    action_responses: list[ActionResponseModel] = Field(
        **ACTION_RESPONSES_FIELD.to_dict(),
        description="Results from executed actions"
    )
```

Integration points:
- Uses [[Reason API Reference|Reason]] for decision tracking
- Uses [[Action Request Message|ActionRequestModel]] for actions
- Uses [[Action Response Message|ActionResponseModel]] for results
- Consumed by Step class for [[Operative API Reference|Operative]] creation

### Step Class

```python
class Step:
    """Utility for managing operatives in steps.
    
    Provides factory methods for creating and configuring Operative
    instances based on step requirements. Handles request/response
    model creation and validation.
    """
```

Key responsibilities:
- Creates [[Operative API Reference|Operative]] instances for steps
- Configures request/response models
- Manages validation settings
- Handles field inheritance

## Request Management

### request_operative()
```python
@staticmethod
def request_operative(
    *,
    operative: Operative = None,  # Base operative to extend
    operative_name: str | None = None,  # Identifier
    reason: bool = False,  # Enable reasoning
    actions: bool = False,  # Enable actions
    request_params: ModelParams | None = None,  # Model params
    parameter_fields: dict[str, FieldInfo] | None = None,
    base_type: type[BaseModel] | None = None,
    field_models: list[FieldModel] | None = None,
    exclude_fields: list[str] | None = None,
    new_model_name: str | None = None,
    field_descriptions: dict[str, str] | None = None,
    inherit_base: bool = True,
    config_dict: dict | None = None,
    doc: str | None = None,
    frozen: bool = False,
    max_retries: int = None,
    auto_retry_parse: bool = True,
    parse_kwargs: dict | None = None,
) -> Operative:
    """Create an Operative instance for request handling.
    
    Creates and configures an Operative instance with the specified
    features enabled (reasoning, actions) and model parameters.
    
    Used by StepModel to create operatives for step execution.
    """
```

Key features:
- Creates [[Operative API Reference|Operative]] instances
- Configures [[Model Params API Reference|ModelParams]]
- Enables [[Reason API Reference|reasoning]]
- Sets up [[Action Request Message|actions]]

Configuration flow:
1. Parameter setup
```python
params = {}
if operative:
    params = operative.model_dump()
    request_params = operative.request_params.model_dump()
    field_models = request_params.field_models
```

2. Field configuration
```python
if reason and REASON_FIELD not in field_models:
    field_models.append(REASON_FIELD)
if actions and ACTION_REQUESTS_FIELD not in field_models:
    field_models.extend([
        ACTION_REQUESTS_FIELD,
        ACTION_REQUIRED_FIELD,
    ])
```

3. Model creation
```python
request_params = ModelParams(**request_params)
params["request_params"] = request_params
return Operative(**params)
```

## Response Management

### respond_operative()
```python
@staticmethod
def respond_operative(
    *,
    operative: Operative,  # Operative to update
    additional_data: dict | None = None,  # Extra response data
    response_params: ModelParams | None = None,  # Response config
    field_models: list[FieldModel] | None = None,  # Extra fields
    frozen_response: bool = False,  # Lock response
    response_config_dict: dict | None = None,  # Config options
    response_doc: str | None = None,  # Documentation
    exclude_fields: list[str] | None = None,  # Fields to skip
) -> Operative:
    """Update an Operative with response configuration.
    
    Configures response handling for an existing Operative instance,
    optionally adding fields and validation rules.
    
    Used after step execution to handle results.
    """
```

Key features:
- Updates [[Operative API Reference|Operative]] instances
- Configures response models
- Handles additional data
- Controls field inheritance

Update flow:
1. Field setup
```python
field_models = field_models or []
if hasattr(operative.response_model, "action_required"):
    field_models.extend([
        ACTION_RESPONSES_FIELD,
        ACTION_REQUIRED_FIELD,
        ACTION_REQUESTS_FIELD,
    ])
if "reason" in operative.response_model.model_fields:
    field_models.extend([REASON_FIELD])
```

2. Type creation
```python
operative = Step._create_response_type(
    operative=operative,
    response_params=response_params,
    field_models=field_models,
    frozen_response=frozen_response,
    response_config_dict=response_config_dict,
    response_doc=response_doc,
    exclude_fields=exclude_fields,
)
```

3. Data update
```python
data = operative.response_model.model_dump()
data.update(additional_data or {})
operative.response_model = operative.response_type.model_validate(data)
```

### _create_response_type()
```python
@staticmethod
def _create_response_type(
    operative: Operative,  # Operative to configure
    response_params: ModelParams | None = None,  # Response config
    response_validators: dict | None = None,  # Custom validators
    frozen_response: bool = False,  # Lock response
    response_config_dict: dict | None = None,  # Config options
    response_doc: str | None = None,  # Documentation
    field_models: list[FieldModel] | None = None,  # Extra fields
    exclude_fields: list[str] | None = None,  # Fields to skip
) -> Operative:
    """Internal helper for response type creation.
    
    Creates and configures response types for Operative instances,
    handling field inheritance and validation setup.
    
    Used by respond_operative() to set up response handling.
    """
```

Key features:
- Creates response types
- Configures validation
- Manages field inheritance
- Sets up documentation

Creation flow:
1. Field setup
```python
field_models = field_models or []
if hasattr(operative.request_type, "action_required"):
    field_models.extend([
        ACTION_RESPONSES_FIELD,
        ACTION_REQUIRED_FIELD,
        ACTION_REQUESTS_FIELD,
    ])
if hasattr(operative.request_type, "reason"):
    field_models.extend([REASON_FIELD])
```

2. Exclusion setup
```python
exclude_fields = exclude_fields or []
exclude_fields.extend(operative.request_params.exclude_fields)
```

3. Type creation
```python
operative.create_response_type(
    response_params=response_params,
    field_models=field_models,
    exclude_fields=exclude_fields,
    doc=response_doc,
    config_dict=response_config_dict,
    frozen=frozen_response,
    validators=response_validators,
)
```

## Implementation Notes

1. Step Management
   - Model definition
   - Field configuration
   - Action tracking
   - Response handling

2. Request Handling
   - Parameter setup
   - Field management
   - Model creation
   - Type safety

3. Response Handling
   - Type creation
   - Data updates
   - Field extension
   - Validation

4. Performance
   - Efficient updates
   - Minimal copying
   - Field reuse
   - Type caching

## Common Patterns

### Operation Breakdown
```python
# Create step with reasoning and actions
step = StepModel(
    title="Data Processing",
    description="Process input data with validation",
    
    # Add reasoning
    reason=Reason(
        title="Validation Required",
        content="Input data needs format validation",
        confidence_score=0.95  # High confidence
    ),
    
    # Define required actions
    action_required=True,
    action_requests=[
        ActionRequestModel(
            function="validate_data",
            arguments={"data": input_data, "schema": schema}
        ),
        ActionRequestModel(
            function="process_data",
            arguments={"data": input_data}
        )
    ]
)
```

### Operative Creation
```python
# Create operative for step
operative = Step.request_operative(
    operative_name="data_processor",
    
    # Enable features
    reason=True,  # Add reasoning fields
    actions=True,  # Add action fields
    
    # Configure model
    request_params=ModelParams(
        field_models=[
            FieldModel(
                name="input_data",
                annotation=dict,
                description="Data to process"
            ),
            FieldModel(
                name="schema",
                annotation=dict,
                description="Validation schema"
            )
        ]
    ),
    
    # Set options
    auto_retry_parse=True,  # Enable retry
    max_retries=3  # Max attempts
)
```

### Response Configuration
```python
# Configure response handling
operative = Step.respond_operative(
    operative=operative,
    
    # Add results
    additional_data={
        "validation_result": {
            "valid": True,
            "errors": []
        },
        "processed_data": processed_data
    },
    
    # Add response fields
    field_models=[
        FieldModel(
            name="validation_result",
            annotation=dict,
            description="Validation outcome"
        ),
        FieldModel(
            name="processed_data",
            annotation=dict,
            description="Processed result"
        )
    ],
    
    # Lock response
    frozen_response=True
)
```

## Protocol Relationships

### Core Integration
- [[Operative API Reference]] - Base operative
- [[Model Params API Reference]] - Parameters
- [[Field Model]] - Fields

### Step System
- [[Action Request Message]] - Requests
- [[Action Response Message]] - Responses
- [[Reason API Reference]] - Reasoning

### Cross-System
- [[Validation API Reference]] - Validation
- [[Type API Reference]] - Type system
- [[Model API Reference]] - Base models

## Implementation References
- [[Operative API Reference]] - Base operative
- [[Model Params API Reference]] - Parameters
- [[Field Model]] - Fields
