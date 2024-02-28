
# API Calls Configurations for LionAGI

Customizing your `lionagi` experience to fit your specific needs is crucial, especially when dealing with the complexity and potential costs associated with using advanced models like gpt-4. This guide provides detailed instructions on configuring your `lionagi` sessions, including model parameters, rate limits, and more.

## Warning

❗❗ **Important**: Engaging API calls with maximum throughput over a large set of data using advanced models, such as gpt-4, can become **EXPENSIVE IN JUST SECONDS**. It's crucial to configure your sessions thoughtfully to manage costs effectively.

## Customizations

You can customize the following aspects of your `lionagi` sessions:

### `llmconfig`

The `llmconfig` allows you to set default model parameters for every API call within a session. Our default configuration is as follows:

```python
{
    'model': 'gpt-4-turbo-preview',
    'frequency_penalty': 0,
    'max_tokens': None,
    'n': 1,
    'presence_penalty': 0,
    'response_format': {'type': 'text'},
    'seed': None,
    'stop': None,
    'stream': False,
    'temperature': 0.7,
    'top_p': 1,
    'tools': None,
    'tool_choice': 'none',
    'user': None
}
```

To change the default behavior for a session, you can either:

- Pass a new `llmconfig` into the `Session`:

    ```python
    llmconfig_ = {...}
    session = li.Session(system, llmconfig=llmconfig_)
    ```

- Or update the config directly in an existing session:

    ```python
    session.llmconfig.update(llmconfig_)
    ```

### `service`

The `service` configuration is essential for integrating and utilizing LLM services efficiently. By default, the service is set to the OpenAI API service with **tier 1** rate limits for the `gpt-4-1104-preview` model.

To adjust rate limits:

```python
from lionagi import Services, Session

service = Services.OpenAI(max_requests=10, max_tokens=10_000, interval=60)
session = Session('you are a helpful assistant', service=service)
```

#### Note on Rate Limits

For detailed information on rate limits, refer to the [OpenAI usage limit documentation](https://platform.openai.com/docs/guides/rate-limits?context=tier-free).

### Multiple API Keys

If you're managing multiple API keys, add them to your `.env` file. To use an alternative key:

```python
import os
from dotenv import load_dotenv
load_dotenv()

api_key2 = os.getenv("OPENAI_API_KEY2")

service = Services.OpenAI(api_key=api_key2)
session = Session('you are a helpful assistant', service=service)
```

#### Sharing `service` Objects

To apply the same `service` object across multiple sessions:

```python
session2 = Session('you are a helpful assistant', service=service)
session3 = Session('you are a helpful assistant', service=service)
```

This approach ensures consistency in rate limiting and API key usage across your sessions.

