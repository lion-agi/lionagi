![PyPI - Version](https://img.shields.io/pypi/v/lionagi?labelColor=233476aa&color=231fc935)  ![Read the Docs](https://img.shields.io/readthedocs/lionagi)  ![PyPI - License](https://img.shields.io/pypi/l/lionagi?color=231fc935) ![PyPI - Downloads](https://img.shields.io/pypi/dm/lionagi?color=blue)



[PyPI](https://pypi.org/project/lionagi/) | [Documentation](https://lionagi.readthedocs.io/en/latest/) | [Discord](https://discord.gg/mzDD5JtYRp)

  
# LionAGI
**Towards Automated General Intelligence**


LionAGI is an **intelligent agent framework** tailored for **big data analysis** with advanced **machine learning** tools. Designed for data-centric, production-level projects. Lionagi allows flexible and rapid design of agentic workflow, customed for your own data. Lionagi `agents` can manage and direct other agents, can also use multiple different tools in parallel.
  
<img width="1002" alt="image" src="https://github.com/lion-agi/lionagi/assets/122793010/3fd75c2a-a9e9-4ab4-8ae9-f9cd71c69aec">


#### Integrate any Advanced Model into your existing workflow.

<img width="1100" alt="Screenshot 2024-02-14 at 8 54 01 AM" src="https://github.com/lion-agi/lionagi/assets/122793010/cfbc403c-cece-49e7-bc3a-015e035d3607">




### Install LionAGI with pip:

```bash
pip install lionagi
```
Download the `.env_template` file, input your appropriate `API_KEY`, save the file, rename as `.env` and put in your project's root directory. 
by default we use `OPENAI_API_KEY`.

 
### Intelligence Services

| Provider | Type | Parallel Chat | Perform Action | Embeddings | MultiModal |
| ---- | ---- | ---- | ---- | ---- | ---- |
| OpenAI | API | ✅ | ✅ |  |  |
| OpenRouter | API | ✅ |  |  |  |
| Ollama | Local | ✅ |  |  |  |
| LiteLLM | Mixed | ✅ |  |  |  |
| HuggingFace | Local | ✅ |  |  |  |
| MLX | Local | ✅ |  |  |  |
| Anthropic | API |  |  |  |  |
| Azure | API |  |  |  |  |
| Amazon | API |  |  |  |  |
| Google | API |  |  |  |  |
| MistralAI | API |  |  |  |  |

### Quick Start

The following example shows how to use LionAGI's `Session` object to interact with `gpt-4-turbo` model:

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
  instruction=instruction, context=context, model="gpt-4-turbo-preview"
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
      instruction=instruction, context=context, model="gpt-4-turbo-preview"
    )
    print(f"Calculation Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

Visit our notebooks for examples. 

LionAGI is designed to be `asynchronous` only, please check python official documentation on how `async` work: [here](https://docs.python.org/3/library/asyncio.html)

---

**Notice**: 
* calling API with maximum throughput over large set of data with advanced models i.e. gpt-4 can get **EXPENSIVE IN JUST SECONDS**,
* please know what you are doing, and check the usage on OpenAI regularly
* default rate limits are set to be 1,000 requests, 100,000 tokens per miniute, please check the [OpenAI usage limit documentation](https://platform.openai.com/docs/guides/rate-limits?context=tier-free) you can modify token rate parameters to fit different use cases.
* if you would like to build from source, please download the [latest release](https://github.com/lion-agi/lionagi/releases),  **main is under development and will be changed without notice**


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

