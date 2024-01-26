Function Calling
================

Function calling is a powerful feature of OpenAI ``gpt-4`` and other models. It essentially is a **Function Picker and
Parameter Provider**. It can help you choose which function, if any, to invoke with which parameters, under provided context and instruction.

LionAGI allows simple usage of function callings in the ``Session`` object.

.. code-block:: python

   import lionagi as li

Here is an example of a function description formatted in the OpenAI schema.

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
                    # specify parameters required for the model to respond when function calling
                    "required": ["number1", "number2"],
                },
            }
        }

   # register both the function description and actual implementation
   def multiply(number1, number2):
        return number1*number2

.. note::

   For more information about OpenAI-hosted tools, please check the `OpenAI tools documentation <https://platform.openai.com/docs/assistants/tools/function-calling>`_

In this example, we are going to tackle a math problem using the multiplication function and enforce the output format
as JSON.

Let's define the necessary message information we need to pass in for our example.

.. code-block:: python

   system = "you are asked to perform as a function picker and parameter provider"

   task = "Think step by step, understand the following basic math question and \
           provide two numbers as parameters for function calling."
   # when using respond_mode as json to enforce output format
   # you need to provide specifying details in instruction
   json_format = {"number1": "x", "number2": "y"}
   instruct1 = {"Task": task, "json_format": json_format}

   question1 = "There are [basketball, football, backpack, water bottle, strawberry, tennis ball, \
               rockets]. each comes in four different colors, \
               what is the number of unique kinds of ball?"
   question2 = "There are three fruits in total, each with 2 different colors, how many unique \
               kinds of fruits are there?"

   context1 = {"Question1": question1, "question2": question2}

   # created a tool object
   tools = li.Tool(func=multiply, schema_=tool_schema)

With all the necessary information in place, we are now ready to construct the session.

To ensure effective management and application of tools within the session, it's crucial to register all the necessary tools.
Additionally, we need to adjust the llmconfig to accommodate any additional setting requirements.

.. code-block:: python

   session = li.Session(system=system)
   session.register_tools(tools)

.. code-block:: python

   # by_default, tools are not used, you need to specify
   # tools = True, allows all tools to be available to use
   await session.chat(instruction=instruct1,
                      context=context1,
                      tools=True,
                      response_format={'type':"json_object"})

Let’s check the message records in this session:

.. code-block:: python

   li.lcall(session.messages.content, lambda x: print(x))

.. code-block:: markdown

   {"system_info": "you are asked to perform as a function picker and parameter provider"}

   {"instruction": {"Task": "Think step by step, understand the following basic math
    question and provide parameters for function calling.", "json_format": {"number1": "x",
    "number2": "y"}}, "context": {"Question1": "There are [basketball, football, backpack,
    water bottle, strawberry, tennis ball, rockets]. each comes in four different colors,
    what is the number of unique kinds of ball?", "question2": "There are three fruits in
    total, each with 2 different colors, how many unique kinds of fruits are there?"}}

   {"action_list": [{"recipient_name": "functions.multiply", "parameters": {"number1": 3,
   "number2": 4}}, {"recipient_name": "functions.multiply", "parameters": {"number1": 3,
   "number2": 2}}]}

   {"action_response": {"function": "multiply", "arguments": {"number1": 3, "number2": 4},
   "output": 12}}

   {"action_response": {"function": "multiply", "arguments": {"number1": 3, "number2": 2},
   "output": 6}}
