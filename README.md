![PyPI - Version](https://img.shields.io/pypi/v/lionagi?labelColor=233476aa&color=231fc935) ![PyPI - Downloads](https://img.shields.io/pypi/dm/lionagi?color=blue)



[PyPI](https://pypi.org/project/lionagi/) | [Documentation](https://ocean-lion.com/Welcome) | [Discord](https://discord.gg/xCkA5ErGmV)

```
Documentation for v0.0.300+ is in progress

To contribute, you need to make a fork first, and then make pull request from your fork. 
```
  
# LionAGI

**Powerful Intelligent Workflow Automation**

LionAGI is an **intelligent agent framework**. Tailored for **big data analysis** in conjunction with advanced **machine learning** tools, designed for data-centric, production-level projects. Lionagi provides a set of robust tools, enabling flexible and rapid design of agentic workflow, for your own data.  


## Why Automating Workflows?

Intelligent AI models such as [Large Language Model (LLM)](https://en.wikipedia.org/wiki/Large_language_model), introduced new possibilities of human-computer interaction. LLMs is drawing a lot of attention worldwide due to its “one model fits all”, and incredible performance. One way of using LLM is to use as search engine, however, this usage is complicated by the fact that LLMs [hallucinate](https://arxiv.org/abs/2311.05232).

What goes inside of a LLM is more akin to a [black-box](https://pauldeepakraj-r.medium.com/demystifying-the-black-box-a-deep-dive-into-llm-interpretability-971524966fdf), lacking interpretability, meaning we don’t know how it reaches certain answer or conclusion, thus we cannot fully trust/rely the output from such a system. 

<img width="500" alt="ReAct flow" src="https://github.com/lion-agi/lionagi/assets/122793010/fabec1eb-fa8e-4ce9-b75f-b7aca4809c0f">


Another approach of using LLM is to treat them as [intelligent agent](https://arxiv.org/html/2401.03428v1), that are equipped with various tools and data sources. A workflow conducted by such an intelligent agent have clear steps, and we can specify, observe, evaluate and optimize the logic for each decision that the `agent` made to perform actions. This approach, though we still cannot pinpoint how LLM output what it outputs, but the flow itself is **explainable**.

LionAGI `agent` can manage and direct other agents, can also use multiple different tools in parallel.

<img width="700" alt="parallel agents" src="https://github.com/lion-agi/lionagi/assets/122793010/ab263a6a-c7cc-40c3-8c03-ba1968df7309">


### Install LionAGI with pip:

```bash
pip install lionagi
```
Download the `.env_template` file, input your appropriate `API_KEY`, save the file, rename as `.env` and put in your project's root directory. 
by default we use `OPENAI_API_KEY`.


### Quick Start

The following example shows how to use LionAGI's `Session` object to interact with `gpt-4-turbo` model:

```python

# define system messages, context and user instruction
system = "You are a helpful assistant designed to perform calculations."
instruction = {"Addition":"Add the two numbers together i.e. x+y"}
context = {"x": 10, "y": 5}

model="gpt-4-turbo-preview"
```

```python
# in interactive environment (.ipynb for example)
from lionagi import Session

calculator = Session(system)
result = await calculator.chat(instruction, context=context, model=model)

print(f"Calculation Result: {result}")
```

```python
# or otherwise, you can use
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

Visit our notebooks for examples. 

LionAGI is designed to be `asynchronous` only, please check python official documentation on how `async` work: [here](https://docs.python.org/3/library/asyncio.html)

---

**Notice**: 
* calling API with maximum throughput over large set of data with advanced models i.e. gpt-4 can get **EXPENSIVE IN JUST SECONDS**,
* please know what you are doing, and check the usage on OpenAI regularly
* default rate limits are set to be 1,000 requests, 100,000 tokens per miniute, please check the [OpenAI usage limit documentation](https://platform.openai.com/docs/guides/rate-limits?context=tier-free) you can modify token rate parameters to fit different use cases.
* if you would like to build from source, please download the [latest release](https://github.com/lion-agi/lionagi/releases),  
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
Python 3.10 or higher. 

