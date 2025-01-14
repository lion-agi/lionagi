# LionAGI Cookbook

## Chapter 1: Building Your First AI Assistant

LionAGI helps you build AI-powered applications quickly and reliably. In this chapter, you'll create a research assistant that:
- Researches topics thoroughly
- Saves findings to files
- Handles conversations naturally
- Manages errors gracefully

### Prerequisites
- Python 3.10 or higher
- Basic Python knowledge
- OpenAI API key

## Setup

### Installation
```bash
# Create environment
python -m venv env
source env/bin/activate  # or `env\Scripts\activate` on Windows

# Install LionAGI and helpers
pip install lionagi python-dotenv
```

### API Setup
```python
import os
from dotenv import load_dotenv

# Load API key from .env file
# Create .env with: OPENAI_API_KEY=your-key
load_dotenv()

# Or set directly (not recommended for production)
os.environ["OPENAI_API_KEY"] = "your-api-key"
```

## Building a Research Assistant

### Basic Assistant
```python
from lionagi import Branch, Model, types

async def research_topic(
    topic: str,
    questions: list[str]
) -> types.Response:
    """Research a topic with specific questions."""
    # Create research assistant
    assistant = Branch(
        name="Researcher",
        system="""You are a research assistant.
        Provide clear, accurate information.
        Support claims with evidence."""
    )
    
    # Configure model
    model = Model(
        provider="openai",
        model="gpt-3.5-turbo",  # or "gpt-4" for more depth
        temperature=0.7  # balance accuracy & creativity
    )
    assistant.add_model(model)
    
    # Research topic
    context = f"Research topic: {topic}"
    responses = []
    
    for question in questions:
        response = await assistant.chat(
            f"{context}\nQuestion: {question}"
        )
        responses.append({
            "question": question,
            "answer": response
        })
    
    return responses

# Usage
import asyncio
import json

async def main():
    # Research AI safety
    topic = "AI Safety"
    questions = [
        "What are the main concerns?",
        "What solutions exist?",
        "What are future challenges?"
    ]
    
    # Get findings
    findings = await research_topic(topic, questions)
    
    # Save results
    with open("ai_safety_research.json", "w") as f:
        json.dump(findings, f, indent=2)
    
    # Print findings
    for finding in findings:
        print(f"\nQ: {finding['question']}")
        print(f"A: {finding['answer']}")

asyncio.run(main())
```

### Advanced Assistant
```python
from lionagi import Branch, Model, types
from datetime import datetime
from pathlib import Path
import json

class ResearchAssistant:
    """Advanced research assistant with persistence."""
    def __init__(
        self,
        name: str = "Researcher",
        model: str = "gpt-3.5-turbo",
        save_dir: str = "research"
    ):
        # Create assistant
        self.assistant = Branch(
            name=name,
            system="""You are a research assistant.
            Provide clear, accurate information.
            Support claims with evidence.
            Ask for clarification if needed."""
        )
        
        # Configure model
        self.model = Model(
            provider="openai",
            model=model,
            temperature=0.7
        )
        self.assistant.add_model(self.model)
        
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Track research
        self.topics: dict[str, list[dict]] = {}
        self._load_history()
    
    def _load_history(self):
        """Load previous research."""
        for file in self.save_dir.glob("*.json"):
            with open(file) as f:
                research = json.load(f)
                self.topics[research["topic"]] = research
    
    async def research_topic(
        self,
        topic: str,
        questions: list[str]
    ) -> dict[str, str]:
        """Research a topic thoroughly."""
        try:
            # Get answers
            answers = {}
            for question in questions:
                response = await self.assistant.chat(
                    f"Regarding {topic}: {question}"
                )
                answers[question] = response
            
            # Save research
            research = {
                "topic": topic,
                "date": datetime.now().isoformat(),
                "questions": questions,
                "answers": answers
            }
            
            # Save to file
            file_path = self.save_dir / f"{topic.lower()}.json"
            with open(file_path, "w") as f:
                json.dump(research, f, indent=2)
            
            # Update tracking
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
    
    async def get_summary(
        self,
        topic: str,
        style: str = "technical"
    ) -> str:
        """Get research summary in style."""
        if topic not in self.topics:
            return f"No research found for: {topic}"
        
        research = self.topics[topic]
        questions = research["questions"]
        answers = research["answers"]
        
        # Generate summary
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
        """Get researched topics."""
        return list(self.topics.keys())
    
    def get_research(
        self,
        topic: str
    ) -> dict | None:
        """Get research for topic."""
        return self.topics.get(topic)

# Usage
async def research_project():
    """Run research project."""
    # Create assistant
    assistant = ResearchAssistant(
        name="AI Researcher",
        model="gpt-4",  # Use GPT-4 for depth
        save_dir="ai_research"
    )
    
    # Research topics
    topics = {
        "AI Safety": [
            "What are the main concerns?",
            "What solutions exist?",
            "What are future challenges?"
        ],
        "Machine Learning": [
            "What are key concepts?",
            "What are best practices?",
            "What are common pitfalls?"
        ]
    }
    
    # Research each topic
    for topic, questions in topics.items():
        print(f"\nResearching: {topic}")
        
        try:
            # Get answers
            answers = await assistant.research_topic(
                topic,
                questions
            )
            
            # Get summary
            summary = await assistant.get_summary(
                topic,
                style="technical"
            )
            
            print("\nFindings:")
            for q, a in answers.items():
                print(f"\nQ: {q}")
                print(f"A: {a}")
            
            print(f"\nSummary: {summary}")
        
        except Exception as e:
            print(f"Error researching {topic}: {str(e)}")
            continue
    
    # Show all research
    print("\nAll Topics:", assistant.get_topics())

# Run project
asyncio.run(research_project())
```

## Best Practices

1. **Assistant Design**
   - Set clear system message
   - Configure model appropriately
   - Handle errors gracefully
   - Save results persistently

2. **Code Structure**
   - Use type hints
   - Handle exceptions
   - Document functions
   - Follow PEP 8

3. **User Experience**
   - Save research results
   - Provide summaries
   - Handle errors nicely
   - Show progress

## Quick Reference
```python
from lionagi import Branch, Model, types

# Create assistant
assistant = Branch(
    name="Assistant",
    system="You are a helpful assistant."
)

# Configure model
model = Model(
    provider="openai",
    model="gpt-3.5-turbo",
    temperature=0.7
)
assistant.add_model(model)

# Chat safely
try:
    response = await assistant.chat("Hello!")
    print(response)
except Exception as e:
    print(f"Error: {str(e)}")
```

## Next Steps

You've learned:
- How to create an AI assistant
- How to research topics thoroughly
- How to save and manage results
- How to handle errors properly

In [Chapter 2](ch2_concepts.md), we'll explore LionAGI's core concepts and architecture.
