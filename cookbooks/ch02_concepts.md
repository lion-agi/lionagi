# LionAGI Cookbook

## Chapter 2: Building a Customer Service Bot

In [Chapter 1](ch01_get_started.md), we built a **research assistant** primarily using the `branch.chat()` method. 

That approach was **single-turn**: each call to `chat()` did **not** add messages to the conversation history. Now, we’ll explore **LionAGI’s** architecture and focus on **multi-turn** usage with `branch.communicate()`, which **does** store messages for continuous dialogue.

---

## 1. Architecture & Design Philosophy

LionAGI is deliberately **modular**. When building a “Customer Service” bot, these key pieces unite:

1. **Branch**  
   - Coordinates a single conversation.  
   - Maintains messages, tools, logs, and references to an **iModel**.  
   - We’ll use `communicate()` for multi-turn conversation memory.

2. **iModel**  
   - Represents a configured LLM endpoint (like GPT-4o, sonnet-3.5, etc.).  
   - Manages concurrency, token usage, and request settings.

3. **Action System** (Optional)  
   - Tools exposed to the LLM for real backend operations (e.g., resetting a password, issuing refunds).  
   - The LLM can “function-call” them if it decides it needs those capabilities.

4. **Messages & Conversation**  
   - `branch.communicate()` automatically **stores** user messages + assistant replies in order, supporting multi-turn memory.  
   - `branch.chat()`, by contrast, is typically a single-turn approach (no automatic message storage).

5. **Logs & Session** (Advanced)  
   - You can attach a `LogManager` or use a `Session` to handle multiple conversation branches and cross-branch communication.  
   - For now, we’ll stick to a single Branch for a single conversation flow.

### High-Level Flow for Customer Service
1. **User** asks a question or describes a problem.  
2. **Branch** uses an **iModel** to generate a reply, storing both the user inquiry and the assistant response in the conversation.  
3. If a function call is needed (e.g., “reset_password”), the Branch’s tool system handles it.  
4. The conversation continues seamlessly: new user messages have context from previous messages because we used `communicate()`.

---

## 2. Example: Building a Basic Customer Service Branch

Here’s a **LionAGI** approach for multi-turn conversation. Let’s define a simple Tool, an iModel, and a Branch that uses `communicate()`.


### 2.1 Configuring an iModel

```python
from lionagi import iModel

customer_service_model = iModel(
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.7,
    # concurrency/rate-limits can be set if needed
)
```

### 2.2 Creating the Branch

```python
from lionagi import Branch

service_branch = Branch(
    name="CustomerService",
    system="""You are a polite customer service agent.
    - Greet the user.
    - Provide helpful info or next steps.
    - Escalate if the issue is out of scope.""",
    chat_model=customer_service_model,
)
```

Key Points
- The system string sets the overall tone and instructions (like a system prompt).
- chat_model is our chosen LLM interface.
- tools includes our password reset functionality.

### 2.3 Handling Multi-turn Inquiries with communicate()

```python
async def handle_inquiry(user_id: str, user_message: str) -> str:
    """
    Takes the user's message and returns an AI response, 
    preserving conversation history for follow-up questions.
    """
    # Provide context if needed (e.g., user_id)
    response = await service_branch.communicate(
        instruction=user_message,
        context={"user_id": user_id}
    )
    return response
```
Why communicate()?
- It automatically adds the user message and the assistant’s reply to the Branch’s conversation log.
- Follow-up calls to communicate() within the same Branch will see the entire conversation so far.
- This is different from branch.chat(), which does not store messages for future turns.

Demo of Multi-Turn Exchange
```python
import asyncio

async def customer_service_demo():
    # 1) First inquiry
    resp1 = await handle_inquiry("User123", "Hi, I forgot my password.")
    print("Assistant says:", resp1)

    # 2) Follow-up inquiry (the user is still locked out)
    resp2 = await handle_inquiry("User123", "I'm still locked out. Help!")
    print("Assistant says:", resp2)

    # 3) Another question, context is still remembered
    resp3 = await handle_inquiry("User123", "Thanks! How do I change my billing address next?")
    print("Assistant says:", resp3)

# asyncio.run(customer_service_demo())
```
Here, each call to handle_inquiry() uses communicate(), building a conversation that retains context across multiple user messages.

## 3. Managing Conversation State & Logs

### 3.1 Automatic Logging

LionAGI automatically log conversation events via a LogManager. You can configure log manager by passing a config at branch creation:

```python
from lionagi import types

log_config = types.LogManagerConfig(
    persist_dir="./logs",
    capacity=10,        # logs are dumped after 10 events (api_call, function_call)
    extension=".json",
    auto_save_on_exit=True,
)
service_branch = Branch(
    name="CustomerService",
    system="""You are a polite customer service agent.
    - Greet the user.
    - Provide helpful info or next steps.
    - Escalate if the issue is out of scope.""",
    chat_model=customer_service_model,
    tools=[reset_password],  # directly pass in the function
    log_config=log_config,
)
```
You can also check the logs as a DataFrame:

```python
df = service_branch.logs.to_df()
print(df.head())
```
3.2 Viewing Stored Conversation

Because we’re using communicate(), the conversation grows with each user message:
```python
# this will produce a formatted dataframe of messages in the conversation
df = service_branch.to_df()

# whereas below will convert all messages data in the conversation into dataframe
df1 = service_branch.messages.to_df()
```
You’ll see System, User, and Assistant roles in chronological order.

## 4. Best Practices

1.	Use communicate() for Multi-turn
    - If you need a persistent conversation across multiple messages, communicate() automatically appends user & assistant messages.
    - chat() is simpler but stateless (no built-in memory), ideal for single-turn Q&A or ephemeral prompts.
2.	Leverage Tools
    - Real customer service might need secure “Check Account,” “Issue Refund,” or “Reset Password.”
    - Wrap each as a Tool or put them in an ActionManager. The LLM can function-call them as needed.
3.	Log Management
    - Set capacity-based dumping or manual triggers to avoid large memory usage.
    - For compliance or analytics, consider storing logs externally (e.g., in a database).
4.	Escalation Strategy
    - If the LLM says “I can’t handle this” or calls “escalate_ticket,” you can hand off to a manager branch or a real agent.
    - Use a Session if you want multiple Branches or multi-agent flows.
5.	Conversation Summaries
    - For longer sessions, you might occasionally summarize prior messages (to keep context concise) or parse them for user satisfaction.

## 5. Quick Reference

Below is a minimal usage pattern focusing on multi-turn communicate(), different from Chapter 1’s single-turn chat():
```python
from lionagi import Branch, iModel

# 1) Model configuration
cs_model = iModel(
    provider="openai",
    model="gpt-4o",
    temperature=0.7
)

# 2) Branch creation
cs_branch = Branch(
    name="CustomerSupport",
    system="You are a friendly agent with memory of previous messages.",
    chat_model=cs_model
)

# 3) Multi-turn conversation
async def quick_demo():
    # First user message
    first_resp = await cs_branch.communicate("Hi, I need help with my account")
    print("Assistant:", first_resp)

    # Follow-up user message
    second_resp = await cs_branch.communicate("I'm also locked out of billing.")
    print("Assistant:", second_resp)
```
Notice how each communicate() call references the same Branch, so user context accumulates.

## 6. Summary & Next Steps

In this chapter, you’ve seen:
- How communicate() differs from chat(): communicate() keeps conversation state for subsequent turns.
- Integrating Tools for real backend actions in a multi-turn scenario.
- Logging conversation history for compliance or analytics.

Coming Up: Chapter 3 explores advanced function calling and tool integration—including custom schemas, concurrency handling, and more. This opens the door to sophisticated customer service workflows, from verifying user details to secure refunds or escalations.
