# LionAGI (Version 0.1)

![PyPI - Version](https://img.shields.io/pypi/v/lionagi?labelColor=233476aa&color=231fc935) ![PyPI - Downloads](https://img.shields.io/pypi/dm/lionagi?color=blue)

[PyPI](https://pypi.org/project/lionagi/) | [Discord](https://discord.gg/xCkA5ErGmV)

> **IMPORTANT NOTE:** This README is for LionAGI version 0.1. For the latest version and ongoing development, please refer to the main branch. The usage patterns and features described here may not be compatible with newer versions.

```
Documentation for v0.1 is archived.

For documentation specific to this version, please refer to the md_docs directory in this branch of the repository.
For the latest version and documentation, please visit the main branch of the LionAGI repository.
```

## LionAGI v0.1

**Powerful Intelligent Workflow Automation**

LionAGI v0.1 is an intelligent agentic workflow automation framework. It introduces advanced ML models into any existing workflows and data infrastructure.

### Features (v0.1)

- Interact with almost any models including local*
- Run interactions in parallel for most models (OpenRouter, OpenAI, Ollama, litellm...)
- Produce structured pydantic outputs with flexible usage**
- Automate workflow via graph based agents
- Use advanced prompting techniques, i.e. ReAct (reason-action)

\* If there are models on providers that have not been configured, you can do so by configuring your own AI providers and endpoints.

\*\* Structured Input/Output, Graph based agent system, as well as more advanced prompting techniques were under active development in this version.

### Goals

- Provide a centralized agent-managed framework for "ML-powered tools coordination".
- Define workflows as ways of coordination and possible paths among nodes (concept of workflow was still in design in this version).
- Utilize intelligence to solve real-life problems.
- Lower the barrier of entry for creating use-case/domain-specific tools.

### Why Automating Workflows?

Intelligent AI models such as [Large Language Model (LLM)](https://en.wikipedia.org/wiki/Large_language_model), introduced new possibilities of human-computer interaction. LLMs drew a lot of attention worldwide due to their "one model fits all" capability and incredible performance. However, using LLMs as search engines is complicated by the fact that they can [hallucinate](https://arxiv.org/abs/2311.05232).

LLMs are often seen as a [black-box](https://pauldeepakraj-r.medium.com/demystifying-the-black-box-a-deep-dive-into-llm-interpretability-971524966fdf), lacking interpretability. We don't know how they reach certain answers or conclusions, thus we cannot fully trust or rely on the output from such a system.

<img width="500" alt="ReAct flow" src="https://github.com/lion-agi/lionagi/assets/122793010/fabec1eb-fa8e-4ce9-b75f-b7aca4809c0f">

Another approach is to treat LLMs as [intelligent agents](https://arxiv.org/html/2401.03428v1), equipped with various tools and data sources. A workflow conducted by such an intelligent agent has clear steps, and we can specify, observe, evaluate and optimize the logic for each decision that the `agent` makes to perform actions. This approach, while still not pinpointing how an LLM produces its outputs, makes the flow itself **explainable**.

LionAGI `agents` can manage and direct other agents, and can also use multiple different tools in parallel.

<img width="700" alt="parallel agents" src="https://github.com/lion-agi/lionagi/assets/122793010/ab263a6a-c7cc-40c3-8c03-ba1968df7309">

### Installation (v0.1)

```bash
pip install lionagi==0.1.2
```

Download the `.env_template` file, input your appropriate `API_KEY`, save the file, rename as `.env` and put in your project's root directory. 
By default, we use `OPENAI_API_KEY`.

### Quick Start (v0.1)

The following example shows how to use LionAGI's `Session` object to interact with the `gpt-4-turbo` model:

```python
# Define system messages, context and user instruction
system = "You are a helpful assistant designed to perform calculations."
instruction = {"Addition": "Add the two numbers together i.e. x+y"}
context = {"x": 10, "y": 5}

model = "gpt-4-turbo-preview"

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

For more examples specific to v0.1, please refer to the notebooks in the md_docs directory of this branch.

LionAGI is designed to be `asynchronous` only. Please check Python's official documentation on how `async` works: [here](https://docs.python.org/3/library/asyncio.html)

---

**Notice**: 
* Calling API with maximum throughput over a large set of data with advanced models (e.g., gpt-4) can get **EXPENSIVE IN JUST SECONDS**.
* Please understand what you are doing and check the usage on OpenAI regularly.
* Default rate limits are set to 1,000 requests, 100,000 tokens per minute. Please check the [OpenAI usage limit documentation](https://platform.openai.com/docs/guides/rate-limits?context=tier-free). You can modify token rate parameters to fit different use cases.
* If you would like to build from source, please download the [appropriate release for v0.1](https://github.com/lion-agi/lionagi/releases).

**Note: This version has been deprecated. Please refer to the main branch for the latest features and improvements.**

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
  version = {0.1}
}
```

### Requirements
Python 3.10 or higher.