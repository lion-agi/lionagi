
# LionAGI Direct Interaction Tutorial

## Introduction

In LionAGI, interactions with AI can be handled in different ways depending on the task at hand. The `Branch.chat` method is useful for natural language processing and generating conversational responses, while `Branch.direct` provides a more structured approach, allowing for detailed control over the interaction process, including planning, scoring, and selecting from multiple choices. This tutorial provides a comparison between these two methods.

## Table of Contents

1. [Setup](#setup)
2. [Context Definition](#context-definition)
3. [Defining Helper Functions](#defining-helper-functions)
4. [Using Branch.chat](#using-branchchat)
5. [Using Branch.direct](#using-branchdirect)
6. [Conclusion](#conclusion)

## Setup

First, let's import the necessary libraries and initialize the LionAGI module.

```python
from IPython.display import Markdown
import lionagi as li
```

## Context Definition

Define the context for our example: a blue whale chasing a big white shark.

```python
context = "a blue whale is chasing a big white shark"
```

## Defining Helper Functions

Define a helper function to nicely print form fields.

```python
def nice_print(form):
    for k, v in form.work_fields.items():
        display(Markdown(f"{k}: \n{v}\n"))
```

## Using Branch.chat

The `Branch.chat` method generates a natural language response based on the provided instruction and context.

```python
# Initialize a branch
branch = li.Branch()

# Generate a response using Branch.chat
out_ = await branch.chat(
    instruction="analyze the situation, what should the whale do?", context=context
)

# Display the output as Markdown
Markdown(out_)
```

Expected Output:

```markdown
To analyze the situation where a blue whale is chasing a big white shark, let's consider several factors:

1. **Behavioral Context**:
   - Blue whales are generally filter feeders and consume krill and small fish. They are not known to chase or hunt sharks.
   - White sharks are apex predators and typically do not have natural predators, especially not from baleen whales like the blue whale.

2. **Possible Reasons for the Chase**:
   - **Curiosity**: The blue whale might be curious about the shark.
   - **Territorial Behavior**: Although rare, the whale might be displaying some form of territorial behavior.
   - **Misdirected Behavior**: The whale could be confused or disoriented, leading to unusual behavior.

3. **Safety and Energy Considerations**:
   - **Energy Expenditure**: Chasing a shark could be energetically costly for the blue whale, which typically conserves energy for long migrations and feeding.
   - **Risk of Injury**: Engaging with a shark could pose a risk of injury to the whale, even if the whale is significantly larger.

4. **Ecological Impact**:
   - Such interactions are uncommon and could indicate unusual environmental conditions or stressors affecting marine life behavior.

Given these points, the blue whale should ideally:

- **Stop the Chase**: To conserve energy and avoid unnecessary risks.
- **Return to Normal Behavior**: Focus on feeding and migration, which are critical for its survival.
- **Monitor the Environment**: If the behavior is due to environmental stressors, it may be beneficial for marine biologists to investigate further.

In conclusion, the blue whale should stop chasing the shark and resume its typical feeding and migratory activities to ensure its well-being and energy conservation.
```

## Using Branch.direct

The `Branch.direct` method allows for a more structured interaction, providing options for planning, scoring, and selecting choices.

```python
# Generate a structured response using Branch.direct
out_ = await branch.direct(
    instruction="analyze the situation, what should the whale do? write a poeticly absurd story",
    context=context,
    clear_messages=True,
    plan=True,
    score=True,
    select=True,
    allow_extension=True,
    select_choices=[
        "run",
        "chase",
        "fight",
        "hide",
        "call for help",
        "stop",
        "dive",
        "swim",
    ],
)
```

Handle potential errors during execution and print the results.

```python
# Display the structured output
forms = [out_]
forms.extend(out_.extension_forms)

for i in forms:
    nice_print(i)
    print("----")
```

Expected Output:

```markdown
task:
Follow the prompt and provide the necessary output.
- Additional instruction: analyze the situation, what should the whale do? write a poeticly absurd story
- Additional context: a blue whale is chasing a big white shark
- Generate a 3-step plan based on the context.
- Allow auto-extension for another 3 rounds.
- Perform scoring according to score range: [0, 10] and precision: integer.
- Select 1 item from the provided choices: ['run', 'chase', 'fight', 'hide', 'call for help', 'stop', 'dive', 'swim'].

answer:
PLEASE_EXTEND

extension_required:
True

plan:
{'step_1': {'plan': 'The blue whale should reflect on the vastness of the ocean and the absurdity of its chase.', 'reason': 'This will set the stage for a poetic and absurd narrative.'}, 'step_2': {'plan': 'The blue whale should then engage in an unexpected activity, such as singing a melancholic song to the moon.', 'reason': 'This adds a layer of poetic absurdity to the story.'}, 'step_3': {'plan': 'Finally, the blue whale should decide on a course of action, such as stopping the chase and pondering the meaning of its pursuit.', 'reason': 'This concludes the story with a reflective and poetic note.'}}

score:
8

selection:
stop

----
task:
Follow the prompt and provide the necessary output.
- Additional instruction: {"plan": "The blue whale should reflect on the vastness of the ocean and the absurdity of its chase.", "reason": "This will set the stage for a poetic and absurd narrative."}
- Additional context: N/A
- Allow auto-extension for another 2 rounds.
- Perform scoring according to score range: [0, 10] and precision: integer.
- Select 1 item from the provided choices: ['run', 'chase', 'fight', 'hide', 'call for help', 'stop', 'dive', 'swim'].

answer:
The blue whale, amidst the vastness of the ocean, ponders the absurdity of its chase. It realizes that in such an expansive and boundless environment, the pursuit seems almost trivial and nonsensical. The whale decides to stop and reflect on the beauty and enormity of its surroundings, embracing the poetic absurdity of its existence.

extension_required:
False

score:
9

selection:
stop

----
```

## Conclusion

In this tutorial, we compared two methods of interaction in LionAGI: `Branch.chat` and `Branch.direct`. While `Branch.chat` generates conversational responses based on natural language input, `Branch.direct` provides a more structured approach, allowing for detailed planning, scoring, and selection processes. Understanding these methods helps in choosing the right approach for different tasks and achieving better control over AI interactions.
