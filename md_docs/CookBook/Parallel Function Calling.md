# Function Calling in LionAGI

Function calling is a powerful feature supported by OpenAI's `gpt-4` and other models. It allows the model to act as a **Function Picker and Parameter Provider**, helping you choose which function to invoke and with what parameters, based on the provided context and instruction. LionAGI makes it simple to use function calling within the [[session]] object.

## Importing LionAGI

To get started, import the LionAGI library:

```python
import lionagi as li
```

## Defining a Function Schema

To use function calling, you need to define a function schema that describes the function and its parameters. Here's an example of a function schema formatted in the OpenAI schema:

```python
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
            "required": ["number1", "number2"],
        },
    }
}
```

## Registering the Function

After defining the function schema, you need to register both the function description and its actual implementation:

```python
def multiply(number1, number2):
    return number1 * number2
```

For more information about OpenAI-formatted [[tool]], please refer to the [OpenAI tools documentation](https://platform.openai.com/docs/assistants/tools/function-calling).

## Example: Math Problem with Function Calling

Let's tackle a math problem using the multiplication function and enforce the output format as JSON. First, define the necessary message information:

```python
system = "You are asked to perform as a function picker and parameter provider"

task = "Think step by step, understand the following basic math question and provide two numbers as parameters for function calling."
json_format = {"number1": "x", "number2": "y"}
instruct1 = {"Task": task, "json_format": json_format}

question1 = "There are [basketball, football, backpack, water bottle, strawberry, tennis ball, rockets]. Each comes in four different colors. What is the number of unique kinds of ball?"
question2 = "There are three fruits in total, each with 2 different colors. How many unique kinds of fruits are there?"

context1 = {"Question1": question1, "Question2": question2}

from lionagi.core.schema import Tool

tools = li.Tool(func=multiply, schema_=tool_schema)
```

## Creating a Session

With the necessary information in place, create a `Session` object and register the tools:

```python
from lionagi import Session

session = Session(system=system)
session.register_tools(tools)
```

## Chatting with Function Calling

To use function calling in the [[mono chat|chat]], set `tools=True` to make all tools available:

```python
await session.chat(instruction=instruct1,
                   context=context1,
                   tools=True,
                   response_format={'type': "json_object"})
```

## Checking Message Records

To check the message records in the session, use the following code:

```python
import lionagi.libs.ln_func_call as func_call

func_call.lcall(session.messages.content, lambda x: print(x))
```

The output will look something like this:

```markdown
{"system_info": "You are asked to perform as a function picker and parameter provider"}

{"instruction": {"Task": "Think step by step, understand the following basic math question and provide parameters for function calling.", "json_format": {"number1": "x", "number2": "y"}}, "context": {"Question1": "There are [basketball, football, backpack, water bottle, strawberry, tennis ball, rockets]. Each comes in four different colors. What is the number of unique kinds of ball?", "Question2": "There are three fruits in total, each with 2 different colors. How many unique kinds of fruits are there?"}}

{"action_list": [{"recipient_name": "functions.multiply", "parameters": {"number1": 3, "number2": 4}}, {"recipient_name": "functions.multiply", "parameters": {"number1": 3, "number2": 2}}]}

{"action_response": {"function": "multiply", "arguments": {"number1": 3, "number2": 4}, "output": 12}}

{"action_response": {"function": "multiply", "arguments": {"number1": 3, "number2": 2}, "output": 6}}
```
