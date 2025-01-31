![PyPI - Version](https://img.shields.io/pypi/v/lionagi?labelColor=233476aa&color=231fc935)
![PyPI - Downloads](https://img.shields.io/pypi/dm/lionagi?color=blue)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)

[Documentation](https://lion-agi.github.io/lionagi/) | [Discord](https://discord.gg/aqSJ2v46vu) | [PyPI](https://pypi.org/project/lionagi/) | [Roadmap](https://trello.com/b/3seomsrI/lionagi)

# LION - Language InterOperable Network

## An Intelligence Operating System

LionAGI is a robust framework for orchestrating multi-step AI operations with precise control. Bring together multiple models, advanced ReAct reasoning, tool integrations, and custom validations in a single coherent pipeline.

## Why LionAGI?

- **Structured**: LLM interactions are validated and typed (via Pydantic).
- **Expandable**: Integrate multiple providers (OpenAI, Anthropic, Perplexity, custom) with minimal friction.
- **Controlled**: Built-in safety checks, concurrency strategies, and advanced multi-step flows—like ReAct with verbose outputs.
- **Transparent**: Real-time logging, message introspection, and easy debugging of tool usage.


## Installation

```
pip install lionagi
```

Dependencies:
	•	aiocahce
  •	aiohttp
	•	jinja2
	•	pandas
	•	pillow
  •	pydantic
	•	python-dotenv
  •	tiktoken

## Quick Start
```python
from lionagi import Branch, iModel

# Pick a model
gpt4o = iModel(provider="openai", model="gpt-4o")

# Create a Branch (conversation context)
hunter = Branch(
  system="you are a hilarious dragon hunter who responds in 10 words rhymes.",
  chat_model=gpt4o,
)

# Communicate asynchronously
response = await hunter.communicate("I am a dragon")
print(response)
```

```
You claim to be a dragon, oh what a braggin'!
```
### Structured Responses

Use Pydantic to keep outputs structured:

```python
from pydantic import BaseModel

class Joke(BaseModel):
    joke: str

res = await hunter.communicate(
    "Tell me a short dragon joke",
    response_format=Joke
)
print(type(response))
print(response.joke)
```
```
<class '__main__.Joke'>
With fiery claws, dragons hide their laughter flaws!
```

### ReAct and Tools

LionAGI supports advanced multi-step reasoning with ReAct. Tools let the LLM invoke external actions:

```python
from lionagi.tools.types import ReaderTool

branch = Branch(chat_model=gpt4o, tools=ReaderTool)
result = await branch.ReAct(
    instruct={
      "instruction": "Summarize my PDF and compare with relevant papers.",
      "context": {"paper_file_path": "/path/to/paper.pdf"},
    },
    extension_allowed=True,     # allow multi-round expansions
    max_extensions=5,
    verbose=True,      # see step-by-step chain-of-thought
)
print(result)
```

The LLM can now open the PDF, read in slices, fetch references, and produce a final structured summary.

### Observability & Debugging
- Inspect messages:
```python
df = branch.to_df()
print(df.tail())
```
- Action logs show each tool call, arguments, and outcomes.
- Verbose ReAct provides chain-of-thought analysis (helpful for debugging multi-step flows).

### Example: Multi-Model Orchestration

```python
from lionagi import Branch, iModel

gpt4o = iModel(provider="openai", model="gpt-4o")
sonnet = iModel(
  provider="anthropic",
  model="claude-3-5-sonnet-20241022",
  max_tokens=1000,                    # max_tokens is required for anthropic models
)

branch = Branch(chat_model=gpt4o)
# Switch mid-flow
analysis = await branch.communicate("Analyze these stats", imodel=sonnet)
```

Seamlessly route to different models in the same workflow.

### optional dependencies

```
pip install "lionagi[tools]"
pip install "lionagi[llms]"
pip install "lionagi[ollama]"
```

## Community & Contributing

We welcome issues, ideas, and pull requests:
- Discord: Join to chat or get help
- Issues / PRs: GitHub

### Citation
```
@software{Li_LionAGI_2023,
  author = {Haiyang Li},
  month = {12},
  year = {2023},
  title = {LionAGI: Towards Automated General Intelligence},
  url = {https://github.com/lion-agi/lionagi},
}
```

**🦁 LionAGI**
> Because real AI orchestration demands more than a single prompt. Try it out and discover the next evolution in structured, multi-model, safe AI.
