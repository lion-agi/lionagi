Function Calling
================

Function calling is a powerful feature of OpenAI ``gpt-4`` and other models. It essentially is a **Function Picker and
Parameter Provider**. It can help you choose which function, if any, to invoke with which parameters, under provided context and instruction.

LionAGI allows simple usage of function callings in the ``Session`` object.

.. code-block:: python

   import lionagi as li

Here is an example of a function description formatted in the OpenAI schema.

.. code-block:: python

   tools = [
        {
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
   ]

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

   question = "There are [basketball, football, backpack, water bottle, strawberry, tennis ball, \
               rockets]. each comes in four different colors, \
               what is the number of unique kinds of ball?"
   context1 = {"Question": question}

With all the necessary information in place, we are now ready to construct the session.

To ensure effective application of tools within the session, it's crucial to register all the necessary tools.
Additionally, we need to adjust the llmconfig to accommodate any additional setting requirements.

.. code-block:: python

   session = li.Session(system=system)

   session.register_tools(tools, multiply)
   session.llmconfig.update({
        "tools": tools,
        "temperature":0.35,
        "tool_choice": "auto",
        "response_format": {'type':'json_object'}
   })

.. code-block:: python

   await session.initiate(instruction=instruct1, context=context1)

Let’s check the message records in this session:

.. code-block:: python

   li.l_call(session.conversation.messages, lambda x: print(str(x) + '\n'))

.. code-block:: markdown

   {'role': 'system', 'content': 'you are asked to perform as a function picker and
     parameter provider'}

   {'role': 'user', 'content': '{"instruction": {"Task": "Think step by step, understand the
    following basic math question and provide two numbers as parameters for function calling.",
    "json_format": {"number1": "x", "number2": "y"}}, "context": {"Question": "There are
    [basketball, football, backpack, water bottle, strawberry, tennis ball, rockets]. each comes
    in four different colors, what is the number of unique kinds of ball?"}}'}

   {'role': 'assistant', 'content': '\n{\n  "tool_uses": [\n    {\n      "recipient_name":
    "functions.multiply",\n      "parameters": {\n        "number1": 3,  "number2": 4\n
     }\n    }\n  ]\n}'}

   {'role': 'assistant', 'content': '{"function": "multiply", "arguments": {"number1": 3,
    "number2": 4}, "output": 12}'}
