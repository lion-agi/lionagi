# Form API Reference

## Class: `Form`

The `Form` class is a subclass of `BaseComponent` and represents a form with input and output fields. It provides functionality for validating and processing input and output data based on the defined fields and their associated validation rules.

### Attributes

- `template_name` (str): The name of the prompt template. Default is "default_form".
- `signature` (str): Signature indicating inputs and outputs. Default is "null".
- `version` (str | float | int | None): The version of the prompt template. Default is None.
- `description` (str | dict[str, Any] | None | Any): The description of the prompt template. Default is None.
- `task` (str | dict[str, Any] | None): The task associated with the prompt template. Default is None.
- `out_validation_kwargs` (dict[str, Any]): Validation kwargs for output. Default is an empty dictionary.
- `in_validation_kwargs` (dict[str, Any]): Validation kwargs for input. Default is an empty dictionary.
- `fix_input` (bool): Whether to fix input. Default is True.
- `fix_output` (bool): Whether to fix output. Default is True.
- `input_fields` (list[str]): Extracted input fields from the signature. Default is an empty list.
- `output_fields` (list[str]): Extracted output fields from the signature. Default is an empty list.
- `choices` (dict[str, list[str]]): Choices available for each template field. Default is an empty dictionary.

### Properties

- `prompt_fields`: Returns the concatenation of input and output fields.
- `instruction_context`: Generates a string representation of the input fields and their descriptions.
- `instruction`: Generates a string representation of the task, input fields, and output fields.
- `instruction_output_fields`: Returns a dictionary mapping output fields to their descriptions.
- `inputs`: Returns a dictionary mapping input fields to their values.
- `outputs`: Returns a dictionary mapping output fields to their values.

### Methods

- `process(in_=None, out_=None)`: Processes the input and output data based on the specified flags.
- `_validate_field_choices(fields, fix_=False)`: Validates the field choices based on the specified fields and fix flag.
- `_validate_input_choices()`: Validates the input choices.
- `_validate_output_choices()`: Validates the output choices.
- `_validate_field(k, v, choices=None, keys=None, fix_=False, **kwargs)`: Validates a specific field based on its type and associated validation rules.
- `_process_input(fix_=False)`: Processes the input data based on the input fields and validation rules.
- `_get_field_attr(k, attr)`: Retrieves the specified attribute value for a given field.
- `_field_has_attr(k, attr)`: Checks if a field has the specified attribute.
- `_field_has_keys(k)`: Checks if a field has keys.
- `_field_has_choices(k)`: Checks if a field has choices.
- `_process_choices(k, v, fix_=False, kwargs=None)`: Processes the choices for a specific field.
- `_process_keys(k, v, fix_=False, kwargs=None)`: Processes the keys for a specific field.
- `_process_response(out_, fix_=fix_output)`: Processes the output data based on the output fields and validation rules.
- `_get_input_output_fields(str_)`: Extracts the input and output fields from the signature string.
- `_prompt_fields_annotation`: Returns a dictionary mapping prompt fields to their annotations.

## Other Functions

- `non_prompt_words` (list[str]): A list of words that are not considered prompt words.

## Imported Modules

- `typing`: Provides support for type hints.
- `pydantic`: Provides support for data validation and serialization.
- `lionagi.libs.convert`: Provides utility functions for data conversion.
- `lionagi.libs.func_call`: Provides utility functions for function calling.
- `lionagi.core.generic.BaseComponent`: Provides the base class for components.
- `lionagi.core.form.field_validator.validation_funcs`: Provides validation functions for form fields.


## Class: `ScoredForm`

^ffad5b

The `ScoredForm` class is a subclass of `Form` and represents a form with additional fields for confidence score and reason.

### Attributes

- `confidence_score` (float | None): A numeric score between 0 to 1 formatted as "num:0.2f". Default is -1.
- `reason` (str | None): A brief reason for the given output. Default is an empty string.


## Class: `ActionForm`

^b3aad2

The `ActionForm` class is a subclass of `ScoredForm` and represents a form for specifying actions and their associated data.

### Attributes

- `action_needed` (bool | None): Indicates whether actions are needed. Default is False.
- `actions` (list[dict | ActionRequest | Any] | None): A list of action(s) to take, each action represented as a dictionary with "function" and "arguments" keys. Default is an empty list.
- `answer` (str | dict | Any | None): The output answer to the questions asked if further actions are not needed. Default is an empty string.
- `signature` (str): The signature string indicating the input and output fields. Default is "sentence -> reason, action_needed, actions, answer".

## Class: `ActionRequest`

The `ActionRequest` class is not defined in the provided code snippet. It is assumed to be defined elsewhere.

## Imported Modules

- `typing`: Provides support for type hints.
- `lionagi.integrations.bridge.pydantic_.pydantic_bridge.Field`: Provides the `Field` class for defining form fields.
- `lionagi.core.form.scored_form.ScoredForm`: Provides the `ScoredForm` class as a base class for `ActionForm`.

Note: The documentation assumes that the necessary imports are available and the referenced modules and classes are properly defined.