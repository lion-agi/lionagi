
# LionAGI `iModel` Tutorial

## Introduction

This tutorial introduces the `iModel` class in the LionAGI framework, which is used to manage AI model configurations and service integrations. The `iModel` class allows for easy interaction with various AI models by providing a structured way to configure, update, and use these models. This guide will cover the creation, configuration, and usage of `iModel` instances within the LionAGI framework.

## Table of Contents

1. [Creating an iModel Instance](#creating-an-imodel-instance)
2. [Checking Attributes](#checking-attributes)
3. [Calling Chat Completion](#calling-chat-completion)
4. [Updating Configuration](#updating-configuration)
5. [Retrieving Model Information](#retrieving-model-information)
6. [Conclusion](#conclusion)
7. [Additional Methods and Attributes](#additional-methods-and-attributes)

## Creating an iModel Instance

The first step is to create an instance of the `iModel` class. The `iModel` class can be configured with various parameters, including the model name, API key, and other settings.

### Example Usage

The following code demonstrates how to create an `iModel` instance with a specified model name.

```python
import lionagi as li

# Create an iModel instance with the GPT-4o model
m1 = li.iModel(model="gpt-4o")
```

## Checking Attributes

After creating an `iModel` instance, you can check its attributes to ensure it has been configured correctly.

### Example Usage

The following code demonstrates how to check if the `iModel` instance has a specific attribute.

```python
# Check if the iModel instance has the attribute 'ln_id'
hasattr(m1, "ln_id")
# Output: True

# Retrieve the ln_id attribute
m1.ln_id
# Output: '6e9640f6498d2e568153316c690aeeac'
```

## Calling Chat Completion

The `iModel` class provides a method to call the chat completion service asynchronously. This method can be used to interact with the model by sending messages and receiving responses.

### Example Usage

The following code demonstrates how to call the chat completion service using the `iModel` instance.

```python
# Define the messages for the chat completion
messages = [
    {"role": "system", "content": "you are a helpful assistant"},
    {"role": "user", "content": "write a 10 word story"},
]

# Call the chat completion service asynchronously
await m1.call_chat_completion(messages)
# Output:
# ({
#   'messages': [{'role': 'system', 'content': 'you are a helpful assistant'},
#     {'role': 'user', 'content': 'write a 10 word story'}],
#   'model': 'gpt-4o',
#   'frequency_penalty': 0,
#   'n': 1,
#   'presence_penalty': 0,
#   'response_format': {'type': 'text'},
#   'temperature': 0.7,
#   'top_p': 1},
#  {'id': 'chatcmpl-9ObrEZOkXpMQcTE4dkXMfAm3XlwYo',
#   'object': 'chat.completion',
#   'created': 1715652424,
#   'model': 'gpt-4o-2024-05-13',
#   'choices': [{'index': 0,
#     'message': {'role': 'assistant',
#      'content': 'Sunset whispered secrets; the ocean waves carried them away forever.'},
#     'logprobs': None,
#     'finish_reason': 'stop'}],
#   'usage': {'prompt_tokens': 22, 'completion_tokens': 13, 'total_tokens': 35},
#   'system_fingerprint': 'fp_729ea513f7'})
```

## Updating Configuration

The configuration of an `iModel` instance can be updated dynamically to change its behavior or settings.

### Example Usage

The following code demonstrates how to update the configuration of an `iModel` instance.

```python
# Update the configuration to set the maximum tokens to 100
m1.update_config(max_tokens=100)

# Retrieve the updated configuration as a dictionary
m1.to_dict()
# Output:
# {
#  'ln_id': '6e9640f6498d2e568153316c690aeeac',
#  'timestamp': '2024-05-14T02:07:04.079320',
#  'provider': 'OpenAI',
#  'api_key': 'sk-r*******************************************SgD6',
#  'endpoint': 'chat/completions',
#  'token_encoding_name': 'cl100k_base',
#  'model': 'gpt-4o',
#  'frequency_penalty': 0,
#  'max_tokens': 100,
#  'n': 1,
#  'presence_penalty': 0,
#  'response_format': {'type': 'text'},
#  'seed': None,
#  'stop': None,
#  'stream': False,
#  'temperature': 0.7,
#  'top_p': 1,
#  'tools': None,
#  'tool_choice': 'none',
#  'user': None
# }
```

## Retrieving Model Information

The `iModel` class provides a method to retrieve all configuration and metadata information about the model instance.

### Example Usage

The following code demonstrates how to retrieve the model information as a dictionary.

```python
# Retrieve the model information as a dictionary
m1.to_dict()
# Output:
# {
#  'ln_id': '6e9640f6498d2e568153316c690aeeac',
#  'timestamp': '2024-05-14T02:07:04.079320',
#  'provider': 'OpenAI',
#  'api_key': 'sk-r*******************************************SgD6',
#  'endpoint': 'chat/completions',
#  'token_encoding_name': 'cl100k_base',
#  'model': 'gpt-4o',
#  'frequency_penalty': 0,
#  'max_tokens': None,
#  'n': 1,
#  'presence_penalty': 0,
#  'response_format': {'type': 'text'},
#  'seed': None,
#  'stop': None,
#  'stream': False,
#  'temperature': 0.7,
#  'top_p': 1,
#  'tools': None,
#  'tool_choice': 'none',
#  'user': None
# }
```

## Conclusion

In this tutorial, we covered the basics of working with the `iModel` class from the LionAGI framework, including creating an instance, checking attributes, calling chat completion, updating configuration, and retrieving model information. By understanding these fundamental operations, you can effectively utilize the `iModel` class in your Python projects.

## Additional Methods and Attributes

The `iModel` class contains several additional methods and attributes that provide more advanced functionality. Below are some of the key additional methods:

### `call_embedding`

Asynchronously call the embedding service.

```python
# Asynchronous method to call the embedding service
await m1.call_embedding("Your text here")
```

### `embed_node`

Embed the content of a node.

```python
# Asynchronous method to embed the content of a node
await m1.embed_node(node, field="content")
```

### TODO: Add More Endpoints

We plan to extend the functionality of the `iModel` class by adding support for more endpoints in the future. This will enable more comprehensive interactions with various AI services. Stay tuned for updates!
