# LionAGI (Version 0.0.1)

![PyPI - Version](https://img.shields.io/pypi/v/lionagi?labelColor=233476aa&color=231fc935) ![PyPI - License](https://img.shields.io/pypi/l/lionagi?color=231fc935) ![PyPI - Downloads](https://img.shields.io/pypi/dm/lionagi?color=blue)

[PyPI](https://pypi.org/project/lionagi/) | [Discord](https://discord.gg/mzDD5JtYRp)

> **IMPORTANT NOTE:** This README is for LionAGI version 0.0.1. For the latest version and ongoing development, please refer to the main branch. The usage patterns and features described here may not be compatible with newer versions.

```
Documentation for v0.0.1 is archived.

For documentation specific to this version, please refer to the md_docs directory in this branch of the repository.
For the latest version and documentation, please visit the main branch of the LionAGI repository.
```

## LionAGI v0.0.1

**Towards Automated General Intelligence**

LionAGI v0.0.1 is a cutting-edge **intelligent agent framework**. It integrates data manipulation with advanced machine learning tools, such as Large Language Models (i.e. OpenAI's GPT). 
- Designed for data-centric, production-level projects,
- dramatically lowers the barrier in creating intelligent, automated systems
- that can understand and interact meaningfully with large volumes of data. 

### Installation (v0.0.1)

```bash
pip install lionagi==0.0.116
```

Download the `.env_template` file, input your appropriate `API_KEY`, save the file, rename as `.env` and put in your project's root directory. 
By default, we use `OPENAI_API_KEY`.

### Features (v0.0.1)

- Create a production ready LLM application **in hours**, with more than 100 models to choose from
- Written in pure python, minimum dependency `aiohttp`, `python-dotenv`, `tiktoken`, `pydantic`
- Efficient and versatile data operations for reading, chunking, binning, writing, storing data with built-in support for `langchain` and `llamaindex`
- Unified interface with any LLM provider, API or local
  - Fast and **concurrent** API call with **configurable rate limit**
  - (Work In Progress) support for hundreds of models both API and local

LionAGI is designed to be `asynchronous` only. Please check Python's official documentation on how `async` works: [here](https://docs.python.org/3/library/asyncio.html)

### Quick Start (v0.0.1)

The following example shows how to use LionAGI's `Session` object to interact with the `gpt-4` model:

```python
import lionagi as li

# define system messages, context and user instruction
system = "You are a helpful assistant designed to perform calculations."
instruction = {"Addition": "Add the two numbers together i.e. x+y"}
context = {"x": 10, "y": 5}

# in interactive environment (.ipynb for example)
calculator = li.Session(system=system)
result = await calculator.initiate(instruction=instruction,
                                   context=context,
                                   model="gpt-4-1106-preview")

print(f"Calculation Result: {result}")

# or otherwise, you can use
import asyncio
from dotenv import loadenv

load_dotenv()

async def main():
    calculator = li.Session(system=system)
    result = await calculator.initiate(instruction=instruction,
                                       context=context, 
                                       model="gpt-4-1106-preview")
    print(f"Calculation Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

For more examples specific to v0.0.1, please refer to the notebooks in the md_docs directory of this branch.

---

**Notice**: 
* Calling API with maximum throughput over a large set of data with advanced models (e.g., gpt-4) can get **EXPENSIVE IN JUST SECONDS**.
* Please understand what you are doing and check the usage on OpenAI regularly.
* Default rate limits are set to be **tier 1** of OpenAI model `gpt-4-1104-preview`. Please check the [OpenAI usage limit documentation](https://platform.openai.com/docs/guides/rate-limits?context=tier-free). You can modify token rate parameters to fit different use cases.
* If you would like to build from source, please download the [appropriate release for v0.0.1](https://github.com/lion-agi/lionagi/releases).

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
  version = {0.0.1}
}
```

### Requirements
Python 3.9 or higher.