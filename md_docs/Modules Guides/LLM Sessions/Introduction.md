

### Core Features of the `Session` Object

#### Message Management and Logging

A session orchestrates the flow of messages within a conversation, tracking system messages, user inputs, and assistant responses. This management is crucial for maintaining the context of an ongoing dialogue and ensuring coherent responses from the AI model.

#### AI Model Inferencing with Services

The session interfaces with `Services` to leverage AI models for generating responses. This feature allows the session to access sophisticated language models, like GPT-4, and apply them to the conversation, ensuring relevant and contextually appropriate outputs.

#### Multi-round Exchange Enablement

Sessions are designed to support complex conversations involving multiple exchanges. By maintaining state across interactions, sessions enable a natural and fluid dialogue between users and the AI, catering to various conversational scenarios.

### Working with Branches

A unique aspect of the `Session` object is its structure, which comprises one or more "branches." Each session starts with a default `'main'` branch. Branches are instrumental in organizing different threads or topics within a broader conversation, allowing for more granular control over the dialogue flow.

- **Branch Messages**: Within a branch, messages are stored in a `pd.DataFrame`, providing a structured and accessible format for analyzing conversation history.

### Creating and Utilizing a Session

#### Creating a Session

To initiate a conversation using LionAGI, you create a `Session` object, optionally specifying system parameters and selecting an AI service for model inference.

```python
from lionagi import Session

# Creating a session with a specified persona
comedian1 = Session("you are sarcastically funny comedian")
```

#### Generating AI Responses

Once a session is established, you can use it to generate responses to user inputs, leveraging the `chat` method to interact with the configured AI model.

```python
# User instruction for the AI
instruct1 = "very short joke: a blue whale and a big shark meet at the bar and start dancing"

# Generating a joke with a maximum token limit
joke1 = await comedian1.chat(instruct1, max_token=50)
```

```python
# Displaying the joke
from IPython.display import Markdown
Markdown(joke1)
```
#### Changing AI Models

The session's flexibility allows for easy switching between different AI models or services, facilitating experimentation with various configurations to achieve the desired conversational quality.

```python
from lionagi import Services

service = li.Services.OpenRouter(
	max_tokens=1000, max_requests=10, interval=60
)

# Specifying a different AI model
model = "mistralai/mistral-7b-instruct"

# Creating a new session with the configured service
comedian2 = Session(
	"you are sarcastically funny comedian", 
	service=service
)

# Generating a response using the new model
joke2 = await comedian2.chat(
	instruct1, model=model, max_token=50
)
```

```python
Markdown(joke2)
```

#### Accessing Conversation History

The messages within a session's branch can be accessed for review or analysis, providing insights into the conversation flow and the AI's performance.

```python
# Accessing the messages in the default branch of the session
comedian2.messages 
comedian2.branches['main'].messages # getting messages from a branch
comedian2.all_messages. # get all messages across all branches
```

