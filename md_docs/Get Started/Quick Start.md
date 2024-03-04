# Quick Start


## Load Environment Variable

Before diving into using LionAGI, you might need to set up your environment variables. If you're using `.env` files for your project, ensure you have the `python-dotenv` package installed:

```shell
pip install python-dotenv
```

Load your environment variables at the beginning of your script or notebook:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Basic Usage

LionAGI is designed to be flexible, supporting both script and interactive (e.g., Jupyter Notebook) environments. Here's how to get started with LionAGI in both contexts.

### Interactive Environment (Jupyter Notebook)

```python
import lionagi as li

# Define your system messages, context, and instructions
system = "You are a helpful assistant designed to perform calculations."
instruction = {"Addition": "Add the two numbers together i.e. x+y"}
context = {"x": 10, "y": 5}

# Create a LionAGI session and perform a chat operation
calculator = li.Session(system=system)
result = await calculator.chat(
	instruction, context=context, model="gpt-4-turbo-preview")

print(f"Calculation Result: {result}")
```

### Script Environment

For running LionAGI in a script, you'll need to use asynchronous programming patterns:

```python
import asyncio
from dotenv import load_dotenv
load_dotenv()

import lionagi as li

async def main():
    system = "You are a helpful assistant designed to perform calculations."
    instruction = {"Addition": "Add the two numbers together i.e. x+y"}
    context = {"x": 10, "y": 5}
    
    calculator = li.Session(system=system)
    result = await calculator.chat(
	instruction, context=context, model="gpt-4-turbo-preview")
    
    print(f"Calculation Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- [[Configuration]]
- [[Concepts]]
- 

