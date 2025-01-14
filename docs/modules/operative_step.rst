=====================================
Operative & Step
=====================================

The **Operative** and **Step** classes in LionAGI provide a **step-based** 
framework for creating and handling **request/response** logic. These classes 
build upon Pydantic-based “model params” to define how data should be parsed, 
validated, and managed as part of a single “operation” or a multi-step 
workflow. They also offer convenience methods for constructing new request 
or response types on the fly, allowing a dynamic approach to typed 
exchanges.


------------------------------
1. Operative (``operative.py``)
------------------------------
.. module:: lionagi.operatives.operative
   :synopsis: Defines the Operative class for typed request/response logic.

.. class:: Operative

   **Inherits from**: :class:`SchemaModel`

   **Purpose**:
- Serves as a flexible container describing how a system should 
  handle request data (input) and produce response data (output).
- References two sets of :class:`ModelParams`: one for the request 
  (:attr:`request_params`) and one for the response (:attr:`response_params`).
- Dynamically generates Pydantic model classes for these sets of parameters.

**Key Attributes**:
- :attr:`request_type` / :attr:`response_type`:
  The actual Pydantic model classes derived from :attr:`request_params`
  and :attr:`response_params`.
- :attr:`response_model`:
  An instance of the response model, storing the final structured data
  (if successfully parsed).
- :attr:`auto_retry_parse`:
  Whether to automatically re-try parsing if the initial parse fails.
- :attr:`max_retries`:
  Maximum attempts at re-parsing or fuzzy matching.
- :attr:`parse_kwargs`:
  Extra arguments for parsing logic (like fuzzy thresholds).

**Key Methods**:

- :meth:`update_response_model(text=None, data=None) -> BaseModel|dict|str|None`  
  Attempt to parse the provided text or dictionary into the operative’s
  response model. The result is stored in :attr:`response_model`.

- :meth:`raise_validate_pydantic(text) -> None`  
  Strictly validates the text by fuzzy-matching fields and raising 
  an error on mismatch.

- :meth:`force_validate_pydantic(text) -> None`  
  More lenient approach that tries to coerce or force unmatched data 
  into the response model.

- :meth:`create_response_type(...) -> None`  
  Creates a new response model type from the provided 
  :class:`ModelParams`, storing it in :attr:`response_type`.

**Usage Example**::

   from lionagi.operatives.operative import Operative
   from lionagi.operatives.models.model_params import ModelParams

   req_params = ModelParams( ... )  # define fields for request
   operative = Operative(request_params=req_params)

   # Suppose you have some string response from an LLM
   text = '{"some_key": "some_value"}'
   operative.update_response_model(text=text)
   print(operative.response_model)
   # => parsed Pydantic model instance (if successful)

The **Operative** class is especially useful when you want to define 
both an expected request format (input) and a response format (output) 
in a typed manner, ensuring the system can parse or validate them 
reliably.


---------------------------
2. Step (``operative.py``)
---------------------------
.. module:: lionagi.operatives.operative
   :synopsis: Contains utility classes for single-step operations.

.. class:: StepModel

   **Inherits from**: :class:`BaseModel`

   An **example** Pydantic model that demonstrates how a single "operational
   step" might look:

   - :attr:`title`: Title or label for the step.
   - :attr:`description`: Additional details or instructions.
   - :attr:`reason`: A :class:`Reason` object capturing optional reasoning.
   - :attr:`action_requests` / :attr:`action_responses`: Potential tool 
     requests or replies associated with the step.
   - :attr:`action_required`: Boolean indicating if the step must 
     involve a tool call.

**Example**::

   from lionagi.operatives.operative import StepModel

   step_data = {
       "title": "Example Step",
       "description": "A sample step requiring user input",
       "action_required": True,
       "action_requests": [{"function": "add", "arguments": {"x": 1, "y": 2}}],
   }
   step = StepModel(**step_data)
   print(step.action_required)  # => True


.. class:: Step
   :noindex:

A **utility** class with static methods to help you build or update
:class:`Operative` objects in a single-step context. For instance:

- :meth:`request_operative(...)`  
  Creates an :class:`Operative` geared towards request-handling
  (optionally adding fields like reason or actions).
- :meth:`respond_operative(...)`  
  Once you have an operative with a known request format, this helps
  define or add the **response** format.

**Example**::

   from lionagi.operatives.operative import Operative
   from lionagi.operatives.operative import Step

   # 1) Create an operative for requests
   op = Step.request_operative(
       operative_name="ExampleOperative",
       reason=True,
       actions=True
   )
   # => returns an Operative configured with reason/actions fields
   # for the request model

   # 2) Once you have a response to parse, you can do:
   op.update_response_model(text='{"some_key": "value"}')
   # => sets op.response_model if parse is successful

   # 3) Or define a brand new response type:
   Step.respond_operative(
       operative=op,
       field_models=[...],
       # ... more config ...
   )


-------------------
Summary
-------------------
- **Operative** is a “two-phase” typed container describing how to handle 
  requests and produce responses, each potentially with advanced fuzz-matching 
  or validation.
- **StepModel** exemplifies a single-step data structure, showing how 
  instructions, reason, and action requests combine in a single chunk.
- **Step** offers a convenience set of methods for creating or updating 
  an :class:`Operative`, bridging the gap between typed Pydantic models 
  and real LionAGI usage, including potential tool calls (action requests).

When building multi-step flows or orchestrating larger tasks, you can 
use these classes to ensure consistent data structures, robust 
validation, and a streamlined approach to request/response handling.
