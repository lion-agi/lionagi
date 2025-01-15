# LionAGI Cookbook

## Chapter 2: Building a Customer Service Bot

In [Chapter 1](ch1_get_started.md), you built a research assistant. Now we'll explore LionAGI's core concepts by building a customer service bot that:
- Handles user inquiries
- Manages conversation state
- Routes requests appropriately
- Tracks user satisfaction

### Prerequisites
- Completed [Chapter 1](ch1_get_started.md)
- Understanding of async/await
- Basic Python knowledge

## Core Concepts

### Message Flow
```python
from lionagi import Branch, Model, types

async def handle_inquiry(
    message: str,
    context: dict = None
) -> types.Response:
    """Handle customer inquiry with context."""
    # Create service agent
    agent = Branch(
        name="CustomerService",
        system="""You are a helpful customer service agent.
        Be polite and professional.
        Ask for clarification when needed.
        Escalate complex issues appropriately."""
    )
    
    # Configure model
    model = Model(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.7  # Balance consistency & flexibility
    )
    agent.add_model(model)
    
    # Add context if provided
    if context:
        context_msg = "\n".join(
            f"{k}: {v}" for k, v in context.items()
        )
        agent.add_context(context_msg)
    
    # Handle inquiry
    response = await agent.chat(message)
    return response

# Usage
import asyncio

async def main():
    # Simple inquiry
    response = await handle_inquiry(
        "How do I reset my password?"
    )
    print("Response:", response)
    
    # Inquiry with context
    response = await handle_inquiry(
        "I can't access my account",
        context={
            "user_id": "12345",
            "last_login": "2023-01-01",
            "account_type": "premium"
        }
    )
    print("Response:", response)

asyncio.run(main())
```

### State Management
```python
from lionagi import Branch, Model, types
from datetime import datetime
from pathlib import Path
import json

class ServiceAgent:
    """Customer service agent with state."""
    def __init__(
        self,
        name: str = "ServiceAgent",
        model: str = "gpt-3.5-turbo",
        log_dir: str = "service_logs"
    ):
        # Create agent
        self.agent = Branch(
            name=name,
            system="""You are a customer service agent.
            Be helpful and professional.
            Track user satisfaction.
            Escalate when needed."""
        )
        
        # Configure model
        self.model = Model(
            provider="openai",
            model=model,
            temperature=0.7
        )
        self.agent.add_model(self.model)
        
        # Setup logging
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Track conversations
        self.conversations: dict[str, list[dict]] = {}
    
    async def handle_message(
        self,
        user_id: str,
        message: str,
        context: dict = None
    ) -> dict:
        """Handle user message with state."""
        try:
            # Get conversation history
            if user_id not in self.conversations:
                self.conversations[user_id] = []
            
            history = self.conversations[user_id]
            
            # Add context
            if context:
                context_msg = "\n".join(
                    f"{k}: {v}" for k, v in context.items()
                )
                self.agent.add_context(context_msg)
            
            # Get response
            response = await self.agent.chat(message)
            
            # Track interaction
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "message": message,
                "response": response,
                "context": context
            }
            
            history.append(interaction)
            
            # Save to log
            log_file = self.log_dir / f"{user_id}.json"
            with open(log_file, "w") as f:
                json.dump(history, f, indent=2)
            
            return {
                "response": response,
                "needs_escalation": "escalate" in response.lower()
            }
        
        except Exception as e:
            # Log error
            error_log = self.log_dir / "errors.json"
            with open(error_log, "a") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id,
                    "error": str(e)
                }, f)
                f.write("\n")
            
            raise e
    
    def get_history(
        self,
        user_id: str
    ) -> list[dict]:
        """Get user conversation history."""
        return self.conversations.get(user_id, [])
    
    async def analyze_satisfaction(
        self,
        user_id: str
    ) -> dict:
        """Analyze user satisfaction."""
        history = self.get_history(user_id)
        if not history:
            return {"error": "No history found"}
        
        # Analyze interactions
        interactions = json.dumps(history, indent=2)
        prompt = f"""
        Analyze customer satisfaction from these interactions:
        {interactions}
        
        Consider:
        - Response tone
        - Issue resolution
        - Follow-up needs
        - Escalation patterns
        """
        
        try:
            analysis = await self.agent.chat(prompt)
            return {
                "user_id": user_id,
                "analysis": analysis,
                "interactions": len(history)
            }
        except Exception as e:
            return {"error": str(e)}

# Usage
async def service_demo():
    """Demo customer service system."""
    # Create agent
    agent = ServiceAgent(
        name="HelpDesk",
        model="gpt-4"  # Use GPT-4 for better service
    )
    
    # Handle inquiries
    user_id = "user123"
    inquiries = [
        "How do I upgrade my account?",
        "The upgrade failed",
        "I want a refund"
    ]
    
    # Process each inquiry
    for inquiry in inquiries:
        print(f"\nUser: {inquiry}")
        
        try:
            # Get response
            result = await agent.handle_message(
                user_id=user_id,
                message=inquiry,
                context={
                    "account_type": "basic",
                    "join_date": "2023-01-01"
                }
            )
            
            print("Agent:", result["response"])
            
            if result["needs_escalation"]:
                print("Note: Needs escalation")
        
        except Exception as e:
            print(f"Error: {str(e)}")
            continue
    
    # Analyze satisfaction
    analysis = await agent.analyze_satisfaction(user_id)
    print("\nSatisfaction Analysis:", analysis)

# Run demo
asyncio.run(service_demo())
```

## Event Handling

### Response Events
```python
from lionagi import Branch, Model, types
from enum import Enum
from typing import Callable

class EventType(Enum):
    INQUIRY = "inquiry"
    RESPONSE = "response"
    ESCALATION = "escalation"
    ERROR = "error"

class EventHandler:
    """Handle service events."""
    def __init__(self):
        self.handlers: dict[EventType, list[Callable]] = {
            event_type: []
            for event_type in EventType
        }
    
    def on(
        self,
        event: EventType,
        handler: Callable
    ):
        """Register event handler."""
        self.handlers[event].append(handler)
    
    async def emit(
        self,
        event: EventType,
        data: dict
    ):
        """Emit event to handlers."""
        for handler in self.handlers[event]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                print(f"Handler error: {str(e)}")

class ServiceAgentWithEvents(ServiceAgent):
    """Service agent with event handling."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = EventHandler()
    
    async def handle_message(
        self,
        user_id: str,
        message: str,
        context: dict = None
    ) -> dict:
        """Handle message with events."""
        # Emit inquiry event
        await self.events.emit(
            EventType.INQUIRY,
            {
                "user_id": user_id,
                "message": message,
                "context": context
            }
        )
        
        try:
            # Get response
            result = await super().handle_message(
                user_id,
                message,
                context
            )
            
            # Emit response event
            await self.events.emit(
                EventType.RESPONSE,
                {
                    "user_id": user_id,
                    "response": result["response"]
                }
            )
            
            # Check escalation
            if result["needs_escalation"]:
                await self.events.emit(
                    EventType.ESCALATION,
                    {
                        "user_id": user_id,
                        "message": message,
                        "response": result["response"]
                    }
                )
            
            return result
        
        except Exception as e:
            # Emit error event
            await self.events.emit(
                EventType.ERROR,
                {
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            raise e

# Usage
async def event_demo():
    """Demo event handling."""
    # Create agent
    agent = ServiceAgentWithEvents()
    
    # Add event handlers
    def log_inquiry(data: dict):
        print(f"\nNew inquiry from {data['user_id']}")
        print(f"Message: {data['message']}")
    
    def log_response(data: dict):
        print(f"\nResponse to {data['user_id']}")
        print(f"Content: {data['response']}")
    
    async def handle_escalation(data: dict):
        print(f"\nEscalation needed for {data['user_id']}")
        print(f"Issue: {data['message']}")
        # Could notify supervisor, create ticket, etc.
    
    def log_error(data: dict):
        print(f"\nError for {data['user_id']}")
        print(f"Details: {data['error']}")
    
    # Register handlers
    agent.events.on(EventType.INQUIRY, log_inquiry)
    agent.events.on(EventType.RESPONSE, log_response)
    agent.events.on(EventType.ESCALATION, handle_escalation)
    agent.events.on(EventType.ERROR, log_error)
    
    # Test events
    await agent.handle_message(
        user_id="user123",
        message="I need a refund immediately!",
        context={"account_type": "premium"}
    )

# Run demo
asyncio.run(event_demo())
```

## Best Practices

1. **State Management**
   - Track conversation history
   - Store context appropriately
   - Log interactions
   - Handle errors gracefully

2. **Event Handling**
   - Use typed events
   - Handle async properly
   - Log event failures
   - Keep handlers focused

3. **User Experience**
   - Maintain conversation context
   - Provide clear responses
   - Handle escalations
   - Track satisfaction

## Quick Reference
```python
from lionagi import Branch, Model, types

# Create service agent
agent = Branch(
    name="Service",
    system="You are a customer service agent."
)

# Configure model
model = Model(
    provider="openai",
    model="gpt-3.5-turbo",
    temperature=0.7
)
agent.add_model(model)

# Handle inquiry
try:
    response = await agent.chat(
        "How can I help you?"
    )
    print(response)
except Exception as e:
    print(f"Error: {str(e)}")
```

## Next Steps

You've learned:
- How to manage conversation state
- How to handle events
- How to track interactions
- How to analyze satisfaction

In [Chapter 3](ch3_internal_tools.md), we'll explore function calling and tool integration.
