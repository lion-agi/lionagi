# LionAGI (Version 0.0.3)

![PyPI - Version](https://img.shields.io/pypi/v/lionagi?labelColor=233476aa&color=231fc935) ![PyPI - Downloads](https://img.shields.io/pypi/dm/lionagi?color=blue)

[PyPI](https://pypi.org/project/lionagi/) | [Discord](https://discord.gg/xCkA5ErGmV)

> **IMPORTANT NOTE:** This README is for LionAGI version 0.0.300+. For the latest version (currently v0.2.5) and ongoing development (v0.3.0), please refer to the main branch. The usage patterns and features described here may not be compatible with newer versions.

```
Documentation for v0.0.3 is archived.

For documentation specific to this version, please refer to the md_docs directory in this branch of the repository.
For the latest version and documentation, please visit the main branch of the LionAGI repository.
```

## LionAGI v0.0.3

**Powerful Intelligent Workflow Automation**

LionAGI v0.0.300+ is an intelligent agentic workflow automation framework. It introduces advanced ML models into existing workflows and data infrastructure.

### Features in v0.0.3

- Interact with various models including local*
- Run interactions in parallel for most models (OpenRouter, OpenAI, Ollama, litellm...)
- Produce structured pydantic outputs with flexible usage**
- Automate workflow via graph-based agents
- Use advanced prompting techniques, i.e., ReAct (reason-action)

### Goals

- Provide a centralized agent-managed framework for "ML-powered tools coordination"
- Define workflows as ways of coordination and possible paths among nodes
- Utilize intelligence to solve real-life problems
- Lower the barrier of entry for creating use-case/domain-specific tools

\* Configuration for unsupported models can be done by setting up your own AI providers and endpoints.

\*\* Structured Input/Output, Graph-based agent system, and advanced prompting techniques were under active development in this version.

### Installation (v0.0.3)

```bash
pip install lionagi==0.0.316
```

Download the `.env_template` file, input your appropriate `API_KEY`, save the file, rename as `.env` and put in your project's root directory. 
By default, we use `OPENAI_API_KEY`.

### Quick Start (v0.0.3)

The following example shows how to use LionAGI's `Session` object to interact with the `gpt-4-turbo` model:

```python
# Define system messages, context and user instruction
system = "You are a helpful assistant designed to perform calculations."
instruction = {"Addition": "Add the two numbers together i.e. x+y"}
context = {"x": 10, "y": 5}

model = "gpt-4o"

# In interactive environment (.ipynb for example)
from lionagi import Session

calculator = Session(system)
result = await calculator.chat(instruction, context=context, model=model)

print(f"Calculation Result: {result}")

# Or otherwise, you can use
import asyncio
from dotenv import load_dotenv

load_dotenv()

from lionagi import Session

async def main():
    calculator = Session(system)
    result = await calculator.chat(instruction, context=context, model=model)

    print(f"Calculation Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

For more examples specific to v0.0.300+, please refer to the notebooks in the md_docs directory of this branch.

LionAGI is designed to be `asynchronous` only. Please check Python's official documentation on how `async` works: [here](https://docs.python.org/3/library/asyncio.html)

---

**Notice**: 
* Calling API with maximum throughput over a large set of data with advanced models (e.g., gpt-4) can get **EXPENSIVE IN JUST SECONDS**.
* Please understand what you are doing and check the usage on OpenAI regularly.
* Default rate limits are set to 1,000 requests, 100,000 tokens per minute. Please check the [OpenAI usage limit documentation](https://platform.openai.com/docs/guides/rate-limits?context=tier-free). You can modify token rate parameters to fit different use cases.
* If you would like to build from source, please download the [appropriate release for v0.0.300+](https://github.com/lion-agi/lionagi/releases).

### Community

While this version is no longer actively developed, you can still engage with the LionAGI community for the latest versions: [Join Our Discord](https://discord.gg/7RGWqpSxze)

### Citation

When referencing LionAGI in your projects or research, please cite:

```bibtex
@software{Li_LionAGI_2023,
  author = {Haiyang Li},
  month = {12},
  year = {2023},
  title = {LionAGI: Towards Automated General Intelligence},
  url = {https://github.com/lion-agi/lionagi},
  version = {0.0.3}
}
```

### Requirements
Python 3.10 or higher.