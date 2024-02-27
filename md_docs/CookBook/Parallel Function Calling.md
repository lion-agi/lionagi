
# Tool

To ensure the smooth execution of function calls within the `Session`
object, it is essential to register tools through the `Tool` object.
This approach facilitates effective management and application of tools.

``` python
import lionagi as li
```

If you already have a well structured schema, you may directly construct
a `Tool` object using the function and the corresponding schema.

``` python
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
```

If you do not want to be bothered by writing a schema, `func_to_tool`
can help you generate a schema and construct a `Tool` object for you.

In the generated schema, parameter types are inferred from the function
type hints, and descriptions are based on the docstring.

Since the schema is crucial for function calling, a well-structured
docstring is essential for the quality of the schema constructed for
you. We currently support Google and reST style docstrings.

``` python
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
```

``` python
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
```

It is crucial to register all tools needed for each branch before using
them. You can register a `Tool` object or a list of `Tool` objects.

``` python
session.register_tools(tool_mul)
# or
session.register_tools([tool_mul])
```

In the following steps, you can specify which tool or set of tools you
want to use in that step.

If you want to specify a single tool to be used in this step, you can
pass in:

-   the name of the tool (str)
-   the `Tool` object
-   a tool schema

If you want to specify a subset of tools, you can pass in a list
containing any of these three types.

By default, no tools will be used. If you want to include all registered
tools in the step, you can add `tools=True`.

``` python
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
```


# Function Calling

Function calling is a powerful feature of OpenAI `gpt-4` and other
models. It essentially is a **Function Picker and Parameter Provider**.
It can help you choose which function, if any, to invoke with which
parameters, under provided context and instruction.

LionAGI allows simple usage of function callings in the `Session`
object.

``` python
import lionagi as li
```

Here is an example of a function description formatted in the OpenAI
schema.

``` python
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
```

::: note
::: title
Note
:::

For more information about OpenAI-hosted tools, please check the [OpenAI
tools
documentation](https://platform.openai.com/docs/assistants/tools/function-calling)
:::

In this example, we are going to tackle a math problem using the
multiplication function and enforce the output format as JSON.

Let\'s define the necessary message information we need to pass in for
our example.

``` python
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
```

With all the necessary information in place, we are now ready to
construct the session.

To ensure effective management and application of tools within the
session, it\'s crucial to register all the necessary tools.
Additionally, we need to adjust the llmconfig to accommodate any
additional setting requirements.

``` python
session = li.Session(system=system)
session.register_tools(tools)
```

``` python
# by_default, tools are not used, you need to specify
# tools = True, allows all tools to be available to use
await session.chat(instruction=instruct1,
                   context=context1,
                   tools=True,
                   response_format={'type':"json_object"})
```

Let's check the message records in this session:

``` python
li.lcall(session.messages.content, lambda x: print(x))
```

``` markdown
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
```
