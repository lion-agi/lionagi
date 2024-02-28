
# LionAGI: **Powerful Intelligent Workflow Automation**



LionAGI is an **intelligent agent framework**, which is a type of [expert systems](http://www.sci.brooklyn.cuny.edu/~kopec/cis718/fall_2005/sdarticle5.pdf) [^1]

Tailored for **big data analysis** in conjunction with advanced **machine learning** tools, designed for data-centric, production-level projects. Lionagi provides a set of robust tools, enabling flexible and rapid design of agentic workflow, for your own data.  


## Why Automating Workflows?

Intelligent AI models such as [Large Language Model (LLM)](https://en.wikipedia.org/wiki/Large_language_model), introduced new possibilities of human-computer interaction. LLMs is drawing a lot of attention worldwide due to its “one model fits all”, and incredible performance. One way of using LLM is to use as search engine, however, this usage is complicated by the fact that LLMs [hallucinate](https://arxiv.org/abs/2311.05232). [^2] [^3]

What goes inside of a LLM is more akin to a [black-box](https://pauldeepakraj-r.medium.com/demystifying-the-black-box-a-deep-dive-into-llm-interpretability-971524966fdf), lacking interpretability, meaning we don’t know how it reaches certain answer or conclusion, thus we cannot fully trust/rely the output from such a system. [^4]

![[ReAct flow.jpg]]

Another approach of using LLM is to treat them as [intelligent agent](https://arxiv.org/html/2401.03428v1), that are equipped with various tools and data sources. A workflow conducted by such an intelligent agent have clear steps, and we can specify, observe, evaluate and optimize the logic for each decision that the `agent` made to perform actions. This approach, though we still cannot pinpoint how LLM output what it outputs, but the flow itself is **explainable**. [^5]

LionAGI `agent` can manage and direct other agents, can also use multiple different tools in parallel.


## Context Aware Auto Workflow Composition

`directive` is a communication system for central control to manage other agentic workflows, it is (currently) designed by human, but made for AI agents. 

it includes the following 

- **LioN Directive Language (LNDL)**: a [Domain Specific Language](https://en.wikipedia.org/wiki/Domain-specific_language) (DSL), defining syntax of communications among agents and workflows. [^6]
- Parsers, Evaluators, Engines, Templates and other supportive components.

![[Picture1.png]]
### Why Another Language?

 [[Function Calling]] in LLM is a powerful feature. In essence, the LLM acts as a configuration provider that can interact with any callable objects, in other words, ability to make decision that can have real impact in our lives. 

Currently, the [[Base Nodes#^0c90e6|tool]] usages are still relatively simple, it requires plenty prompt engineering and with relatively pretty “static” usages. LLM can decide what to call, whether to call, and what to call on, but that’s about it. 

With directive, we hope to add more flexibility and dynamics in tool usages, and enable context aware auto workflow composition. We believe this will have positive effects on agents’

- quality of “planning” in a resource constrained environment 
- ability in mastering domain specific tasks with general purpose models 
- “creativity” in problem solving


> Haiyang Li, ocean@lionagi.ai, Feb 2024

### Next Steps

- [[Installation and Setup]]
- [[Quick Start]]
- [[Modules Guides/LLM Sessions/Introduction|Introduction to LLM session]]
- [[RAG - Auto Research]]



##### REFERENCES

[^1]: Liao, S.-H. (2004). [Expert system methodologies and applications—a decade review from 1995 to 2004](http://www.sci.brooklyn.cuny.edu/~kopec/cis718/fall_2005/sdarticle5.pdf). _Expert Systems with Applications_, volume(28), page 93. 
[^2]: Wikipedia contributors. (Feb 27, 2024). [Large language model](https://en.wikipedia.org/wiki/Large_language_model). _Wikipedia_.
[^3]: Huang, L., Yu, W., Ma, W., Zhong, W., Feng, Z., Wang, H., Chen, Q., Peng, W., Feng, X., Qin, B., & Liu, T. (2023). [A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions](https://arxiv.org/abs/2311.05232). _arXiv preprint arXiv:2311.05232_.
[^4]: Raj, P. D. (Date of publication). [Demystifying the Black Box: A Deep Dive into LLM Interpretability.](https://pauldeepakraj-r.medium.com/demystifying-the-black-box-a-deep-dive-into-llm-interpretability-971524966fdf) _Medium_. 
[^5]: Cheng, Y., Zhang, C., Zhang, Z., Meng, X., Hong, S., Li, W., Wang, Z., Wang, Z., Yin, F., Zhao, J., & He, X. (2024). [Exploring Large Language Model based Intelligent Agents: Definitions, Methods, and Prospects](https://arxiv.org/abs/2401.03428v1). _arXiv:2401.03428v1 [cs.AI]_
[^6]: Wikipedia contributors. (Feb 6, 2024). [Domain-specific language](https://en.wikipedia.org/wiki/Domain-specific_language). _Wikipedia_