# LionAGI Cookbook

## Chapter 1: Building Your First AI Assistant

LionAGI helps you build AI-powered applications quickly and reliably. In this chapter, you'll create a **research assistant** that:

- Researches topics thoroughly  
- Saves findings to files  
- Handles conversations naturally  
- Manages errors gracefully  

---

### Prerequisites
- Python 3.10 or higher  
- Basic Python knowledge  
- OpenAI API key  

---

## 1. Setup

### 1.1 Installation

```bash
# Create a virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install LionAGI and dotenv
pip install lionagi
```
### 1.2 API Setup

```python
import os
from dotenv import load_dotenv

# Load API key from .env file
# Create a .env file containing:
# OPENAI_API_KEY=your-key
load_dotenv()

# Alternatively, set directly (not recommended for production):
os.environ["OPENAI_API_KEY"] = "your-api-key"
```

## 2. Building a Basic Assistant

The Basic Assistant shows how to query GPT-based models with LionAGI. We’ll ask a few questions about AI Safety as an example.
```python
from timeit import default_timer as timer

start = timer()

import lionagi

print(f"Imported lionagi in {timer()-start:.3f} seconds")
print(f"lionagi version: {lionagi.__version__}")
```
if this code runs without errors, you have successfully installed LionAGI.

```python
from lionagi import Branch, iModel
from IPython.display import display, Markdown

# 1. Configure the AI model
ai_model = iModel(
    provider="openai",
    model="gpt-4o-mini",  # Example model identifier
    temperature=0.7,      # Balances accuracy & creativity
    invoke_with_endpoint=False,
)

# 2. Create the 'Researcher' assistant branch
assistant = Branch(
    name="Researcher",
    system="""You are a research assistant.
    Provide clear, accurate information.
    Support claims with concise evidence.""",
    chat_model=ai_model,
)

# 3. Define the topic and questions
topic = "AI Safety"
questions = [
    "What are the main concerns?",
    "What solutions exist?",
    "What are future challenges?",
]

# 4. Conduct the research
context = f"Research topic: {topic}"
responses = []

for question in questions:
    # Prompt the assistant with context and question
    response = await assistant.chat(f"{context}\nQuestion: {question}")

    # Display the response in a Jupyter Notebook (if using IPython)
    display(Markdown(response))

    # Store the response
    responses.append({"question": question, "answer": response})
```


Explanation:
1.	iModel configures how we interact with OpenAI. We specify the model name and temperature.
2.	Branch sets up a conversational context (the system prompt).
3.	assistant.chat() sends queries (prompts) to GPT.
4.	We collect results in responses, which you can later print or save.

3. Building an Advanced Assistant

## 3. Building an Advanced Assistant

Now let’s expand on the basic approach. The Advanced Assistant adds:
1.	Persistent storage for research (JSON files)
2.	Error handling (API key issues, rate limits)
3.	Summaries of research topics
4.	Retrieval of previously saved topics

```python
from lionagi import Branch, iModel
from datetime import datetime
from pathlib import Path
import json


class ResearchAssistant:
    """Advanced research assistant with persistence."""

    def __init__(
        self,
        name: str = "Researcher",
        model: str = "gpt-4o-mini",
        save_dir: str = "research",
    ):
        # 1. Configure the AI model
        ai_model = iModel(provider="openai", model=model, temperature=0.7)

        # 2. Create the assistant branch
        self.assistant = Branch(
            name=name,
            system="""You are a research assistant.
            Provide clear, accurate information.
            Support claims with evidence.
            Ask for clarification if needed.""",
            chat_model=ai_model,
        )

        # 3. Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

        # 4. Track research in memory
        self.topics: dict[str, dict] = {}
        self._load_history()

    def _load_history(self):
        """
        Loads previous research from JSON files in the save_dir.
        Each file is expected to be named after the topic, e.g. "ai_safety.json".
        """
        for file in self.save_dir.glob("*.json"):
            with open(file) as f:
                research = json.load(f)
                self.topics[research["topic"]] = research

    async def research_topic(
        self, topic: str, questions: list[str]
    ) -> dict[str, str]:
        """
        Researches a topic thoroughly by asking multiple questions.
        Returns a dictionary of {question -> answer}.
        """
        try:
            answers = {}
            for question in questions:
                response = await self.assistant.chat(
                    f"Regarding {topic}: {question}"
                )
                answers[question] = response

            # Save research to a JSON file
            research = {
                "topic": topic,
                "date": datetime.now().isoformat(),
                "questions": questions,
                "answers": answers,
            }

            file_path = (
                self.save_dir / f"{topic.lower().replace(' ', '_')}.json"
            )
            with open(file_path, "w") as f:
                json.dump(research, f, indent=2)

            # Update in-memory tracking
            self.topics[topic] = research

            return answers

        except Exception as e:
            # Handle common errors
            if "API key" in str(e):
                raise ValueError(
                    "Invalid API key. Please check your configuration."
                )
            elif "Rate limit" in str(e):
                raise ValueError(
                    "Rate limit exceeded. Please try again later."
                )
            else:
                raise e

    async def get_summary(self, topic: str, style: str = "technical") -> str:
        """
        Generates a summary of the answers for a researched topic in a specific style.
        Returns the summary string, or an error if the topic was not found.
        """
        if topic not in self.topics:
            return f"No research found for: {topic}"

        research = self.topics[topic]
        questions = research["questions"]
        answers = research["answers"]

        prompt = f"""
        Summarize research on {topic}.
        Style: {style}
        Questions covered: {', '.join(questions)}
        Key findings: {json.dumps(answers, indent=2)}
        """

        try:
            return await self.assistant.chat(prompt)
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def get_topics(self) -> list[str]:
        """Returns a list of all topics researched so far."""
        return list(self.topics.keys())

    def get_research(self, topic: str) -> dict | None:
        """Returns the full research details for a given topic, or None if not found."""
        return self.topics.get(topic)
```

Usage Example
:
```python
from IPython.display import display, Markdown

async def research_project():
    """Demonstrates how to use the advanced ResearchAssistant."""

    # 1. Create an instance of ResearchAssistant
    assistant = ResearchAssistant(
        name="AI Researcher", model="gpt-4o", save_dir="ai_research"
    )

    # 2. Define topics and questions
    topics = {
        "AI Safety": [
            "What are the main concerns?",
            "What solutions exist?",
            "What are future challenges?",
        ],
        "Machine Learning": [
            "What are key concepts?",
            "What are best practices?",
            "What are common pitfalls?",
        ],
    }

    # 3. Research each topic
    for topic, questions in topics.items():
        print(f"\nResearching: {topic}")

        try:
            # Gather answers
            answers = await assistant.research_topic(topic, questions)

            # Generate and print a summary
            summary = await assistant.get_summary(topic, style="technical")

            print("\nFindings:")
            for q, a in answers.items():
                display(Markdown(f"**Q**: {q}"))
                display(Markdown(f"**A**: {a}"))

            display(Markdown(f"\nSummary:\n{summary}"))

        except Exception as e:
            print(f"Error researching {topic}: {str(e)}")
            continue

    # 4. Show all researched topics
    display(Markdown(f"\nAll Topics:{assistant.get_topics()}"))

# If you’re running in an environment that supports async,
# you can execute:
# await research_project()
# else you can use:
# asyncio.run(research_project())
```
```python
# Example call (in an async environment, such as Jupyter Notebook):
await research_project()
```
Explanation
1.	ResearchAssistant Class: Encapsulates functions to query GPT, track and load previous research, and generate summaries.
2.	_load_history(): Loads prior research from JSON files in save_dir.
3.	research_topic(): Prompts GPT with each question, saves answers to a local JSON file, and updates an internal topics dictionary.
4.	get_summary(): Builds a customized summary prompt and returns GPT’s response.
5.	Error Handling: Uses Python exceptions to catch and respond to common issues (invalid key, rate limits).

## 4. Best Practices
1.	Assistant Design
- Provide a clear system message (role, instructions, style).
- Configure model parameters (model, temperature) carefully.
- Gracefully handle common errors (API key problems, rate limits).
2.	Code Structure
- Use type hints for clarity (e.g., -> dict[str, str]).
- Keep code modular and documented.
- Follow PEP 8 style guidelines.
3.	User Experience
- Persist research results so users can revisit them.
- Offer summaries or highlights.
- Provide progress/error notifications to guide the user.

5. Quick Reference

A minimal snippet for reference:
```python
from lionagi import Branch, iModel

# Configure model
ai_model = iModel(
    provider="openai",
    model="gpt-3.5-turbo",
    temperature=0.7
)

# Create an assistant
assistant = Branch(
    name="Assistant",
    system="You are a helpful assistant.",
    chat_model=ai_model
)

# Safe chat
try:
    response = await assistant.chat("Hello!")
    print(response)
except Exception as e:
    print(f"Error: {str(e)}")
```

## 6. Next Steps

You have now learned:
1.	How to create a Basic AI Assistant
2.	How to research topics, save results, and manage errors
3.	How to retrieve and summarize past research

In Chapter 2, we’ll explore LionAGI’s core concepts and dive deeper into its architecture.

You’ll learn how to handle more complex conversation flows, manipulate prompts dynamically, and use advanced features like multiple branches or streaming responses.

Happy coding and researching!
