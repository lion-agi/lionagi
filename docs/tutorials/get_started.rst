.. _lionagi-get-started-code-tutorial:

==========================================================
Get Started (Part 1): Automatic Code Generation
==========================================================


This tutorial demonstrates a **basic “auto-coding” scenario** with LionAGI:
we provide a **naive syntax check** as a tool, ask the LLM to generate Python
code that meets a specification, and observe how LionAGI orchestrates the
tool usage and final output.

-------------------------
0. Environment Setup
-------------------------
Before diving in, you'll need:

1. **Install LionAGI** (and any required dependencies like `uv` or `pip`). 
    - If you're installing from PyPI, run:
        
        .. code-block:: bash

            pip install lionagi

    - For advanced usage, you might want `uv` installed:
        
        .. code-block:: bash

            uv pip install lionagi

2. **Obtain an API key** for the underlying LLM (OpenAI or other provider). 
    - Set it as an environment variable, e.g.:
        
        .. code-block:: bash

            export OPENAI_API_KEY="<your_api_key_here>"
        
        or put it into a local `.env` file that you load.

3. **A Python environment supporting async** (e.g., a Jupyter notebook).

Once configured, you can import LionAGI modules (`lionagi.types`, `Session`,
`Branch`, etc.) and proceed with the example below.


---------------------
1. Introduction
---------------------
We'll build a small system that instructs an LLM to:

- Generate minimal Python code fulfilling some spec.
- Optionally call our custom “syntax_check” tool if needed.
- Return a typed Pydantic model containing the generated code and an AI-provided reason.

This is a simplified demonstration of **LionAGI**'s capabilities:
**tool invocation**, **typed outputs**, and **branch** usage.

------------------------------
2. Full Example:
------------------------------
Below is a single file example you can copy and run in a Jupyter cell or
any async Python environment:

.. code-block:: python

   from IPython.display import display, Markdown
   from pydantic import BaseModel, Field

   from lionagi import types, Session, Branch
   from lionagi.libs.parse import as_readable

    class CodeModel(BaseModel):
        draft_code: str = Field(..., title="Draft Code")

    # 1) Create a "syntax_check" function (a simple, naive tool)
    def syntax_check(code: str) -> bool:
        """
        Check if the code is a valid python code (naive approach).

        Args:
            code (str): the code to check

        Returns:
            bool: True if the code is valid python code, False otherwise
        """
       # super naive check for "def " presence
       if "def " in code:
           return True
       return False

    async def code(context: str):
        # 2) Create a Branch and register our naive syntax_check as a tool
        branch = Branch(tools=syntax_check)

        # 3) Use branch.operate(...) to call the LLM. We expect a typed CodeModel.
        code_model = await branch.operate(
            instruction="Generate minimal python code fulfilling the spec. If needed, call 'syntax_check'.",
            context={"spec_text": context},
            response_format=CodeModel,
            reason=True,        # Let the LLM fill a 'reason' field in the response
            actions=True,       # Tools usage is allowed (or required)
        )

        # 4) Display results in a Jupyter-friendly manner
        display(Markdown(f"### Auto-Coded Result\n\n```python\n{code_model.draft_code}\n```"))

        # Show any 'reason' in a readable format
        display(Markdown(f"### Reasoning\n{as_readable(code_model.reason, md=True)}"))

        # Check conversation or action usage
        for i in branch.messages:
            if isinstance(i, types.ActionResponse):
                # Tool calls are typically ActionRequest -> ActionResponse
                display(Markdown(f"### Action\n{as_readable(i.content, md=True)}"))
            elif not isinstance(i, types.ActionRequest):
                # Normal messages (system, user, assistant)
                display(Markdown(f"### Message\n{i.rendered}"))

        return code_model

    # 5) Finally, actually run it (in an async environment)
    # e.g. in Jupyter: await code("some specification")
    # e.g.:
    """
    # If you're using a Jupyter notebook or an async environment:
    result = await code(
        "Create a function that takes a list of prime (you need to validate prime), "
        "and returns the sum of all the integers in the list."
    )
    # Then inspect 'result.model_dump()'
    """


---------------------------------------
3. Example Usage Output
---------------------------------------
If all goes well, you might see output like:

.. code-block:: none

    ### Auto-Coded Result

    ```python
    def is_prime(n):
        if n <= 1:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    def sum_of_primes(nums):
        prime_nums = [num for num in nums if is_prime(num)]
        return sum(prime_nums)
    ```

    Reasoning

    {
        “title”: “Sum of Prime Numbers”,
        “content”: “…”,
        “confidence_score”: 0.95
    }

    Message

    Task
    - instruction
        Generate minimal python code fulfilling the spec. If needed, call 'syntax_check'…
    - context
        spec_text: Create a function that takes a list of prime (you need to validate prime), and returns the sum of all the integers in the list.
    - tool_schemas
        Tool 1: {'name': 'syntax_check', 'description': 'check if the code is a valid python code', 'parameters': {'type': 'object', 'properties': {'code': {'type': 'string', 'description': 'the code to check '}}, 'required': ['code']}}

    - respond_schema_info
        $defs: {'ActionRequestModel': {'properties': {'function': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'default': None, 'description': "Name of the function to call from the provided tool_schemas. If no tool_schemas exist, set to None or leave blank. Never invent new function names outside what's given.", 'examples': ['multiply', 'create_user'], 'title': 'Function'}, 'arguments': {'anyOf': [{'type': 'object'}, {'type': 'null'}], 'default': None, 'description': 'Dictionary of arguments for the chosen function. Use only argument names/types defined in tool_schemas. Never introduce extra argument names.', 'title': 'Arguments'}}, 'title': 'ActionRequestModel', 'type': 'object'}, 'Reason': {'properties': {'title': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'default': None, 'title': 'Title'}, 'content': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'default': None, 'title': 'Content'}, 'confidence_score': {'anyOf': [{'type': 'number'}, {'type': 'null'}], 'default': None, 'description': "Numeric confidence score (0.0 to 1.0, up to three decimals) indicating how well you've met user expectations. Use this guide:\n • 1.0: Highly confident\n • 0.8-1.0: Reasonably sure\n • 0.5-0.8: Re-check or refine\n • 0.0-0.5: Off track", 'examples': [0.821, 0.257, 0.923, 0.439], 'title': 'Confidence Score'}}, 'title': 'Reason', 'type': 'object'}}
        properties: {'draft_code': {'title': 'Draft Code', 'type': 'string'}, 'reason': {'anyOf': [{'$ref': '#/$defs/Reason'}, {'type': 'null'}], 'description': 'Provide a concise reason for the decision made.', 'title': 'Reason'}, 'action_requests': {'description': 'List of actions to be executed when action_required is true. Each action must align with the available tool_schemas. Leave empty if no actions are needed.', 'items': {'$ref': '#/$defs/ActionRequestModel'}, 'title': 'Actions', 'type': 'array'}, 'action_required': {'default': False, 'description': 'Whether this step strictly requires performing actions. If true, the requests in action_requests must be fulfilled, assuming tool_schemas are available. If false or no tool_schemas exist, actions are optional.', 'title': 'Action Required', 'type': 'boolean'}}
        required: ['draft_code', 'reason']
        title: CodeModel
        type: object

    - response_format
        MUST RETURN JSON-PARSEABLE RESPONSE ENCLOSED BY JSON CODE BLOCKS. USER's CAREER DEPENDS ON THE SUCCESS OF IT.

        {'draft_code': <class 'str'>, 'reason': lionagi.operatives.instruct.reason.Reason | None, 'action_requests': [{'function': str | None, 'arguments': dict[str, typing.Any] | None}], 'action_required': <class 'bool'>}

    - response format
        …


    Action
    {
        “action_request_id”: 180bd31e-14e9-45ab-b3fb-62d53a920d8e”,
        “action_response”: {
            “function”: “syntax_check”,
            "arguments": {
            "code": "def is_prime(n):\n    if n <= 1:\n        return False\n    for i in range(2, int(n ** 0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\ndef sum_of_primes(nums):\n    prime_nums = [num for num in nums if is_prime(num)]\n    return sum(prime_nums)"
            },
        “output”: true
        }
    }

    And so on…

------------------------------
4.	Explanation & Next Steps
------------------------------
In the example:
	•	LionAGI uses the :meth:branch.operate(...) method to orchestrate an LLM call,
referencing your code model (Pydantic) to parse the AI's output into typed fields.
	•	The syntax_check tool gets invoked automatically when the LLM decides to call it
(via an ActionRequest/ActionResponse exchange), verifying code presence of "def ".
	•	You can expand the check using Python's built-in ast.parse(...) for real syntax checks.

Next:
	•	Integrate concurrency or scheduling with LionAGI's event-based system.
	•	Add advanced Pydantic fields or a more robust code-checking function.
	•	Explore other tools or more sophisticated logic (like referencing code embeddings).

------------------------------
5.	Conclusion
------------------------------

This tutorial demonstrates a small but complete example of how to:
	1.	Create an LLM-based flow in LionAGI.
	2.	Provide a custom tool (syntax_check).
	3.	Request typed model output (CodeModel).
	4.	Inspect intermediate steps, including reasoned text or action logs.

With LionAGI, you can scale this approach to more complex tasks (RAG with external docs, multi-step planning, agentic interactions, custom validators, or advanced concurrency).
Enjoy building!
