
### Expanding the Comedian Example

We'll continue with the comedian example, adding layers to the interaction by introducing a session for a critic who will evaluate the comedian's jokes.


```python
from lionagi import Session

comedian = Session("you are sarcastically funny comedian")

instruct1 = """
	very short joke: a blue whale and a big shark meet 
	at the bar and start dancing
"""

# Extending the joke with another instruction
instruct2 = """
	continue the joke: and then they stopped
"""
```

```python
# chat with LLM
joke1 = await comedian.chat(instruct1)
joke2 = await comedian.chat(instruct2)
```

#### Introducing a Critic Session

Next, we introduce a new session with a critic persona to evaluate the comedian's work. This showcases how LionAGI can handle complex interactions involving multiple perspectives.

```python
critic = Session("you are artistically logical commentator")

# Providing context for the critic to evaluate the joke
context = {
    "joke1": {"prompt": instruct1, "response": joke1},
    "joke2": {"prompt": instruct2, "response": joke2}
}

instruct3 = """
	short comments, what do you think about the first joke?
"""

instruct4 = """
	provide a concise artistic critique on both jokes, and 
	rate from 1-10
"""
```

```python
# just need to provide same context once, conversation is tracked
comment1 = await critic.chat(instruct3, context=context)
comment2 = await critic.chat(instruct4)
```

#### Feedback Integration and Improvement

With the critiques received, we then feed this feedback back into the comedian session, illustrating a reflective process where the comedian considers the feedback to refine their jokes.

```python
# Integrating critic feedback into the comedian session for reflection and improvement
instruct5 = """
	your jokes were evaluated by a critic, 
	does it make sense to you? why?
"""

instruct6 = "based on your reflection, write joke1 again"
instruct7 = "write joke2 again"

context2 = {"comments": comment1, "rating": comment2}
```

```python
# Reflecting on and revising the jokes
reflect = await comedian.chat(instruct5, context=context2)
joke11 = await comedian.chat(instruct6)
joke22 = await comedian.chat(instruct7)
```

### Saving and Analyzing Conversations

Finally, LionAGI enables the export of session messages to formats like CSV, facilitating further analysis or record-keeping of the conversational dynamics.

```python
# Exporting messages to CSV for both sessions
comedian.to_csv_file('comedian.csv')
comedian.log_to_csv('comedian_api_log.csv')

critic.to_csv_file('comedian.csv')
critic.log_to_csv('comedian_api_log.csv')
```
