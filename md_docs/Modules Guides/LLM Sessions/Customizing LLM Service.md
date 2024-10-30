Diving into the customization and concurrency aspects of LionAGI sessions, this guide highlights the flexibility of the [[Get Started/Session/Session|session]] object in accommodating various use cases through custom configurations and managing concurrent operations efficiently.

### Customizing Session Behavior

LionAGI's `Session` offers extensive customization options to tailor the behavior of language model (LLM) API calls and manage rate limits effectively.

#### Customizing Services

LionAGI supports multiple services, including `OpenAI` and `OpenRouter`, with additional options in development. These services can be customized to fit specific requirements, such as API key configuration, token encoding, and rate limits.

**Quick Start with Services:**

```python
from lionagi import Services

# Using API services
service_openai = Services.OpenAI()
service_openrouter = Services.OpenRouter()

# using local models
service_transformer = Services.Transformers(model='...')
service_ollam = Services.Ollama(model='...')
service_mlx = Services.MLX(model='...')
```

**Configuring API Services:**

You can configure services by specifying parameters like `api_key`, `key_scheme`, and rate limits (`max_tokens`, `max_requests`, `interval`).

#### Modifying LLM Configuration

The `llmconfig` setting allows you to define default model parameters for API calls within a session. This configuration can be set during session creation or updated later.

**Example Configuration:**

```python
llmconfig_ = {
    # Replace with your actual configuration
    'model': 'gpt-4-turbo-preview',
    'max_tokens': 100,
    # Additional parameters...
}

# Creating a session with custom llmconfig
session1 = li.Session("you are a helpful assistant", llmconfig=llmconfig_)

# Or updating llmconfig later
session1.default_branch.llmconfig.update(llmconfig_)
```

### Rate-Limited Concurrency

Managing concurrency efficiently is crucial for optimizing performance and adhering to service rate limits. LionAGI sessions can handle concurrent operations, enabling parallel processing of multiple scenarios.

#### Implementing a Conditional Calculator Session

Let's illustrate concurrency with a calculator session example, performing operations based on conditions and then running multiple scenarios in parallel.

**Single Scenario Execution:**

```python
from timeit import default_timer as timer

system = """
	You are asked to perform as a calculator.
	Return only a numeric value.
"""

# Defining instructions based on conditions
instruct1 = "add the two numbers"
instruct2 = {"if positive": "times 2", "else": "plus 2"}

start = timer()

# Creating a session and executing steps
calculator = li.Session([[system#^2711f6|System]])

step1 = await calculator.chat(instruct1, context=context)
step2 = await calculator.chat(instruct2)

# Measuring execution time
duration = timer() - start
```
