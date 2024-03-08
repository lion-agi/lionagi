LionAGI introduces a sophisticated approach to function calling within the `Session` object, leveraging the capabilities of AI models like OpenAI's GPT-4 to act as a **Function Picker and Parameter Provider**. This feature enables dynamic selection of functions and parameters based on the provided context and instructions, enhancing the versatility of AI-driven applications.

### Utilizing Function Calling in LionAGI Sessions

Function calling in LionAGI allows for the integration of custom logic into conversational flows, where the AI model can determine which function to invoke and with what parameters, based on the conversation's context.

#### Defining a Tool Schema

To utilize function calling effectively, you must first define a tool schema that outlines the function's name, description, parameters, and any requirements for those parameters.

**Example Schema and Function:**

```python
import lionagi.core.message.schema

tool_schema = {
    "type": "function",
    "function": {
        "name": "multiply",
        "description": "Perform multiplication on two numbers",
        "parameters": {
            "type": "object",
            "properties": {
                "number1": {"type": "number", "description": "a number to multiply"},
                "number2": {"type": "number", "description": "a number to multiply"},
            },
            "required": ["number1", "number2"],
        },
    }
}


def multiply(number1, number2):
    return number1 * number2


# Creating a Tool object with the defined schema
tools = lionagi.core.message.schema.Tool(func=multiply, schema_=tool_schema)
```

#### Preparing the Session

With the tool defined, you can prepare the session to handle function calling by specifying the system message, instruction, and context.

**Example Session Setup:**

```python
system = "you are asked to perform as a function picker and parameter provider"
task = "Understand the math question and provide parameters for function calling."

instruct1 = {"Task": task, "json_format": {"number1": "x", "number2": "y"}}
context1 = {"Question1": question, "Question2": question2}

# Creating a Session with the defined system message and tools
session = li.Session(system=system, tools=tools)
```

#### Invoking Function Calling

To invoke function calling, specify how you want the AI model to format the response, either allowing the model to choose automatically or forcing a function call with specific tool choices.

**Example Function Call Invocation:**

```python
response = await session.chat(
    instruct1,
    context=context1,
    tools=True,  # Enabling tool usage
    response_format={'type': "json_object"}  # Enforcing JSON object response format
)

# Accessing the action request from the response
print(response['action_request'])
```

#### Handling Parallel Function Calls

For scenarios requiring multiple function calls based on the session's response, you can use `lcall` to process these calls in parallel, showcasing LionAGI's ability to handle complex data processing workflows.

**Example Parallel Processing:**

```python
# Processing action requests in parallel
li.lcall(response['action_request'], lambda x: print(x))
```

#### Analyzing Session Messages

The session messages, stored in a pandas DataFrame, provide a structured view of the conversation, including any function calls made and responses received.

**Accessing and Processing Session Messages:**

```python
# Iterating over recent session messages to access action responses
for content in session.default_branch.messages['content'][-2:]:
    print(li.as_dict(content)['action_response'])
```

### Conclusion

Function calling within LionAGI sessions opens up a realm of possibilities for integrating custom logic and decision-making processes into AI-driven conversations. By defining tool schemas, preparing sessions for function calling, and leveraging LionAGI's flexible session management capabilities, developers can create more intelligent, responsive, and context-aware applications. This guide exemplifies the power of LionAGI in enhancing conversational AI with advanced function calling and parameter management techniques.