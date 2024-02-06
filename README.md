![PyPI - Version](https://img.shields.io/pypi/v/lionagi?labelColor=233476aa&color=231fc935)  ![Read the Docs](https://img.shields.io/readthedocs/lionagi)  ![PyPI - License](https://img.shields.io/pypi/l/lionagi?color=231fc935) ![PyPI - Downloads](https://img.shields.io/pypi/dm/lionagi?color=blue)



[PyPI](https://pypi.org/project/lionagi/) | [Documentation](https://lionagi.readthedocs.io/en/latest/) | [Discord](https://discord.gg/mzDD5JtYRp)

  
# LionAGI
**Towards Automated General Intelligence**


LionAGI is a cutting-edge **intelligent agent framework**. It integrates data manipulation with advanced machine learning tools, such as Large Language Models (i.e. OpenAI's GPT). 
- Designed for data-centric, production-level projects,
- dramatically lowers the barrier in creating intelligent, automated systems
- that can understand and interact meaningfully with large volumes of data. 

Install LionAGI with pip:

```bash
pip install lionagi
```
Download the `.env_template` file, input your appropriate `API_KEY`, save the file, rename as `.env` and put in your project's root directory. 
by default we use `OPENAI_API_KEY`.



### Features
- Robust and scalable. Create a production ready LLM application **in hours**, with more than 100 models
- Efficient and verstile data operations for reading, chunking, binning, writing, storing data with support for `langchain` and `llamaindex`
- Built-in support for **chain/graph-of-thoughts, ReAct, Concurrent parallel function calling** 
- Unified interface with any LLM provider, API or local
  - Fast and **concurrent** API call with **configurable rate limit**
  - (Work In Progress) support for models both API and local
---
LionAGI is designed to be `asynchronous` only, please check python official documentation on how `async` work: [here](https://docs.python.org/3/library/asyncio.html)


**Notice**: 
* calling API with maximum throughput over large set of data with advanced models i.e. gpt-4 can get **EXPENSIVE IN JUST SECONDS**,
* please know what you are doing, and check the usage on OpenAI regularly
* default rate limits are set to be **tier 1** of OpenAI model `gpt-4-1104-preview`, please check the [OpenAI usage limit documentation](https://platform.openai.com/docs/guides/rate-limits?context=tier-free) you can modify token rate parameters to fit different use cases.
* if you would like to build from source, please download the [latest release](https://github.com/lion-agi/lionagi/releases),  **main is under development and will be changed without notice**


### Quick Start

The following example shows how to use LionAGI's `Session` object to interact with `gpt-4` model:

```python

# define system messages, context and user instruction
system = "You are a helpful assistant designed to perform calculations."
instruction = {"Addition":"Add the two numbers together i.e. x+y"}
context = {"x": 10, "y": 5}
```

```python
# in interactive environment (.ipynb for example)
import lionagi as li

calculator = li.Session(system=system)
result = await calculator.chat(
  instruction=instruction, context=context, model="gpt-4-1106-preview"
)

print(f"Calculation Result: {result}")
```

```python
# or otherwise, you can use
import asyncio
from dotenv import load_dotenv

load_dotenv()

import lionagi as li

async def main():
    calculator = li.Session(system=system)
    result = await calculator.chat(
      instruction=instruction, context=context, model="gpt-4-1106-preview"
    )
    print(f"Calculation Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

Visit our notebooks for our examples. 

### Community

We encourage contributions to LionAGI and invite you to enrich its features and capabilities. Engage with us and other community members [Join Our Discord](https://discord.gg/7RGWqpSxze)

### Citation

When referencing LionAGI in your projects or research, please cite:

```bibtex
@software{Li_LionAGI_2023,
  author = {Haiyang Li},
  month = {12},
  year = {2023},
  title = {LionAGI: Towards Automated General Intelligence},
  url = {https://github.com/lion-agi/lionagi},
}
```


### Requirements
Python 3.9 or higher. 

