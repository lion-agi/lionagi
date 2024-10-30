# Quick Start


## Basic Usage

LionAGI is designed to be flexible, supporting both script and interactive (e.g., Jupyter Notebook) environments. Here's how to get started with LionAGI in both contexts.

### Interactive Environment (Jupyter Notebook)

```python
from lionagi import Sesison

system = "You are a helpful assistant designed to perform calculations."
instruction = {"Addition": "Add the two numbers together i.e. x+y"}
context = {"x": 10, "y": 5}

# Create a LionAGI session and perform a chat operation
calculator = Session([[system#^2711f6|System]])
result = await calculator.chat(
	instruction, context=context, model="gpt-4-turbo"
)

print(f"Calculation Result: {result}")
```

### Script Environment

For running LionAGI in a script, you'll need to use asynchronous programming patterns:

```python
import asyncio
from dotenv import load_dotenv
load_dotenv()

from lionagi import Sesison

async def main():
    calculator = Session([[system#^2711f6|System]])
    result = await calculator.chat(
		instruction, context=context, model="gpt-4-turbo"
	)

    print(f"Calculation Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```
