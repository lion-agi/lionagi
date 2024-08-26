# LionAGI (Version 0.0.2+)

![PyPI - Version](https://img.shields.io/pypi/v/lionagi?labelColor=233476aa&color=231fc935) ![PyPI - License](https://img.shields.io/pypi/l/lionagi?color=231fc935) ![PyPI - Downloads](https://img.shields.io/pypi/dm/lionagi?color=blue)

[PyPI](https://pypi.org/project/lionagi/) | [Discord](https://discord.gg/mzDD5JtYRp)

> **IMPORTANT NOTE:** This README is for LionAGI version 0.0.2+, with the last iteration being 0.0.211. For the latest version and ongoing development, please refer to the main branch. The usage patterns and features described here may not be compatible with newer versions.

```
Documentation for v0.0.2+ is archived.

For documentation specific to this version, please refer to the md_docs directory in this branch of the repository.
For the latest version and documentation, please visit the main branch of the LionAGI repository.
```

## LionAGI v0.0.2+

**Towards Automated General Intelligence**

LionAGI v0.0.2+ is an **intelligent agent framework** tailored for **big data analysis** with advanced **machine learning** tools. Designed for data-centric, production-level projects, LionAGI allows flexible and rapid design of agentic workflow, customized for your own data. LionAGI `agents` can manage and direct other agents, and can also use multiple different tools in parallel.

<img width="1002" alt="image" src="https://github.com/lion-agi/lionagi/assets/122793010/3fd75c2a-a9e9-4ab4-8ae9-f9cd71c69aec">

#### Integrate any Advanced Model into your existing workflow.

<img width="1100" alt="Screenshot 2024-02-14 at 8 54 01 AM" src="https://github.com/lion-agi/lionagi/assets/122793010/cfbc403c-cece-49e7-bc3a-015e035d3607">

### Installation (v0.0.2+)

```bash
pip install lionagi==0.0.211
```

Download the `.env_template` file, input your appropriate `API_KEY`, save the file, rename as `.env` and put in your project's root directory. 
By default, we use `OPENAI_API_KEY`.

### Quick Start (v0.0.2+)

The following example shows how to use LionAGI's `Session` object to interact with the `gpt-4-turbo` model:

```python
# Define system messages, context and user instruction
system = "You are a helpful assistant designed to perform calculations."
instruction = {"Addition": "Add the two numbers together i.e. x+y"}
context = {"x": 10, "y": 5}

# In interactive environment (.ipynb for example)
import lionagi as li

calculator = li.Session(system=system)
result = await calculator.chat(
  instruction=instruction, context=context, model="gpt-4-turbo-preview"
)

print(f"Calculation Result: {result}")

# Or otherwise, you can use
import asyncio
from dotenv import load_dotenv

load_dotenv()

import lionagi as li

async def main():
    calculator = li.Session(system=system)
    result = await calculator.chat(
      instruction=instruction, context=context, model="gpt-4-turbo-preview"
    )
    print(f"Calculation Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

For more examples specific to v0.0.2+, please refer to the notebooks in the md_docs directory of this branch.

LionAGI is designed to be `asynchronous` only. Please check Python's official documentation on how `async` works: [here](https://docs.python.org/3/library/asyncio.html)

---

**Notice**: 
* Calling API with maximum throughput over a large set of data with advanced models (e.g., gpt-4) can get **EXPENSIVE IN JUST SECONDS**.
* Please understand what you are doing and check the usage on OpenAI regularly.
* Default rate limits are set to 1,000 requests, 100,000 tokens per minute. Please check the [OpenAI usage limit documentation](https://platform.openai.com/docs/guides/rate-limits?context=tier-free). You can modify token rate parameters to fit different use cases.
* If you would like to build from source, please download the [appropriate release for v0.0.2+](https://github.com/lion-agi/lionagi/releases).

**Note: This version has been deprecated, and many features have been removed. The project's future focus is on agent-only functionality.**

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
  version = {0.0.2+}
}
```

### Requirements
Python 3.9 or higher.