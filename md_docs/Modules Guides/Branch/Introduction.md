
LionAGI's `Session` object has evolved to support working with multiple branches, enhancing the ability to manage complex conversational flows and experimental setups within a single session. This guide will delve into how to effectively utilize branches in LionAGI, from creating and managing branches to applying them in sophisticated conversational models.

### Working with Branches in LionAGI Sessions

#### Creating New Branches

Each session starts with a default `'main'` branch. You can create additional branches to explore different conversational paths or experimental scenarios.

**Example: Creating a New Branch**

```python
import lionagi as li

system = "you are asked to perform as a function picker and parameter provider"
session = li.Session(system=system)

# Create a new branch named 'branch1'
session.new_branch('branch1')

# Verify the creation of the new branch
print(session.branches)
```

#### Switching the Default Branch

By default, method calls on the session object interact with the `default_branch`. You can switch the default branch as needed.

**Example: Switching the Default Branch**

```python
# Switch the default branch to 'branch1'
session.change_default('branch1')

# Confirm the switch
print(session.default_branch_name, session.default_branch)
```

### Registering Tools to Branches

Tools, such as custom functions for multiplication and addition, need to be registered to the relevant branches to be utilized within those conversational flows.

**Example: Registering Tools to Specific Branches**

```python
# Define and create tool objects
tool_mul = li.Tool(func=multiply, schema_=tool_1[0])  # Assuming multiply function and schema are defined
tool_add = li.Tool(func=add, schema_=tool_2[0])  # Assuming add function and schema are defined

# Register tool_mul to 'main' branch
session.branches['main'].register_tools(tool_mul)

# Register tool_add to 'branch1' (current default branch)
session.register_tools(tool_add)
```

### Utilizing Branches in Conversational Flows

When interacting with the session, you can specify which branch to use for each conversation. This flexibility allows for parallel development of different conversational strategies within the same session.

**Example: Using Branches for Different Conversational Contexts**

```python
# Define instruction and context for different questions
instruct = {"Task": task, "json_format": json_format}  # Assuming task and json_format are defined
context1 = {"Question1": question, "question2": question2}  # Assuming questions are defined
context2 = {"Question3": question3}  # Assuming question3 is defined

# Chat in 'main' branch
response_main = await session.chat(instruction=instruct, context=context1, to_='main', tools=True)

# Chat in 'branch1' without needing to specify the branch (since it's the default)
response_branch1 = await session.chat(instruction=instruct, context=context2, tools=True)
```

### Merging and Deleting Branches

You can merge the content from one branch into another and delete branches that are no longer needed.

**Example: Merging and Deleting Branches**

```python
# Merge 'branch1' into 'main'
session.merge_branch(from_='branch1', to_='main', update=True, del_=False)

# Switch to 'main' before deleting 'branch1'
session.change_default('main')

# Delete 'branch1'
session.delete_branch('branch1')
```

### Conclusion

The branching feature in LionAGI's `Session` object offers a powerful way to organize and manage complex conversational experiments and flows. By creating, managing, and utilizing branches, developers can explore various conversational strategies in parallel, optimize conversational models, and refine the user experience. This guide highlights the steps and strategies for effectively employing branches within your LionAGI projects, enabling nuanced control over your conversational AI development process.