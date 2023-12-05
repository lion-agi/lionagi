# LionAGI
**Towards Automated General Intelligence**

LionAGI is a Python package that combines data manipulation with AI tools, aiming to simplify the integration of advanced machine learning tools, such as Large Language Models (i.e. OpenAI's GPT).

Install LionAGI with pip:

```bash
pip install lionagi
```
Download the `.env_template` file, input your OPENAI_API_KEY, save the file, rename as `.env` and put in your project's root directory. 
### Features

- Efficient data operations for reading, chunking, binning, writing, storing and managing data.
- Robust integration with LLM services like OpenAI with configurable rate limiting concurrent API calls for efficiency and maximum throughput. 
- Create a production ready LLM application in hours. Intuitive workflow management to streamline and expedite the process from idea to market.

Currently, LionAGI only natively support OpenAI API calls, support for other LLM providers as well as open source will be integrated in future releases.



### Quick Start

The following simplified example demonstrates how to use LionAGI to perform a calculation by handling a workflow:

```python
import lionagi as li

# define system messages, context and user instruction
system = "You are a helpful assistant designed to perform calculations."
instruction = {"Addition":"Add the two numbers together i.e. x+y"}
context = {"x": 10, "y": 5}

# Initialize a session with a system message
calculator = li.Session(system=system)

# run a LLM API call
result = await calculator.initiate(instruction=instruction, context=context, model="gpt-4-1106-preview")

print(f"Calculation Result: {result}")
```

Visit our notebooks for our examples. 

### Community

We encourage contributions to LionAGI and invite you to enrich its features and capabilities. Review our [contribution guidelines](https://github.com/lion-agi/lionagi/CONTRIBUTING.md) for more information. Engage with us and other community members on [Discord](https://discord.gg/your-invite-link).

### License

LionAGI is released under the [MIT License](https://github.com/lion-agi/lionagi/LICENSE).

### Contact

- Official Discord Channel
- [ocean@lionagi.ai](mailto:ocean@lionagi.ai)
- [GitHub Repository](https://github.com/lion-agi/lionagi)

### Citation

When referencing LionAGI in your projects or research, please cite:

```bibtex
@software{Li_LionAGI_2023,
  author = {Haiyang Li},
  month = {12},
  year = {2023},
  title = {LionAGI: Towards Automated Intelligence},
  url = {https://github.com/lion-agi/lionagi},
}
```
Thank you for choosing LionAGI. 
