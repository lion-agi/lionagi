Tool
====

To ensure the smooth execution of function calls within the ``Session`` object, it is essential to register tools
through the ``Tool`` object. This approach facilitates effective management and application of tools.

.. code-block:: python

   import lionagi as li

If you already have a well structured schema, you may directly construct a ``Tool`` object using the function
and the corresponding schema.

.. code-block:: python

   tool_schema = {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Perform multiplication on two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "number1": {
                        "type": "number",
                        "description": "a number to multiply, e.g. 5.34",
                    },
                    "number2": {
                        "type": "number",
                        "description": "a number to multiply, e.g. 17",
                    },
                },
                # specify which parameters are required for the model to respond when function calling
                "required": ["number1", "number2"],
            },
        }
    }

   def multiply(number1, number2):
       return number1*number2

   tool_mul = li.Tool(func=multiply, schema_=tool_1[0])

If you do not want to be bothered by writing a schema, ``func_to_tool`` can help you generate a schema and construct
a ``Tool`` object for you.

In the generated schema, parameter types are inferred from the function type hints, and descriptions are based on the
docstring.

Since the schema is crucial for function calling, a well-structured docstring is essential for the quality of the schema
constructed for you. We currently support Google and reST style docstrings.

.. code-block:: python

   # google style docstring (default)
   def multiply(number1:float, number2:float):
       '''
       Perform multiplication on two numbers.

       Args:
           number1: a number to multiply, e.g. 5.34
           number2: a number to multiply, e.g. 17

       Returns:
           The product of number1 and number2.

       '''
       return number1*number2

   tool_mul = li.func_to_tool(multiply)

.. code-block:: python

   # reST style docstring
   def multiply(number1:float, number2:float):
       '''
       Perform multiplication on two numbers.

       :param number1: a number to multiply, e.g. 5.34
       :param number2: a number to multiply, e.g. 17
       :returns:  The product of number1 and number2.
       '''
       return number1*number2

   tool_mul = li.func_to_tool(multiply, docstring_style='reST')

It is crucial to register all tools needed for each branch before using them.
You can register a ``Tool`` object or a list of ``Tool`` objects.

.. code-block:: python

   session.register_tools(tool_mul)
   # or
   session.register_tools([tool_mul])

In the following steps, you can specify which tool or set of tools you want to use in that step.

If you want to specify a single tool to be used in this step, you can pass in:

- the name of the tool (str)
- the ``Tool`` object
- a tool schema

If you want to specify a subset of tools, you can pass in a list containing any of these three types.

By default, no tools will be used. If you want to include all registered tools in the step, you can add ``tools=True``.

.. code-block:: python

   # all compatible inputs

   # default: no tools will be used
   await session.chat(instruction=instruct)

   # use all registered tools
   await session.chat(instruction=instruct, tools=True)

   # name
   await session.chat(instruction=instruct, tools='multiply')

   # list of name
   await session.chat(instruction=instruct, tools=['multiply'])

   # tool
   await session.chat(instruction=instruct, tools=tool_mul)

   # list of tool
   await session.chat(instruction=instruct, tools=[tool_mul])

   # schema
   await session.chat(instruction=instruct, tools=tool_schema)

   # list of schema
   await session.chat(instruction=instruct, tools=[tool_schema])

