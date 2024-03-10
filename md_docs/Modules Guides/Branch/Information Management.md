The advanced functionalities of LionAGI's `Session` object extend into detailed branch management, including accessing branch information, filtering messages, and editing branch content. These features enable granular control over the conversational flow, allowing developers to analyze, modify, and extend conversations within a branch dynamically.

### Accessing Branch Information

LionAGI provides comprehensive methods to access detailed information about a branch's conversational history, including descriptive statistics, specific instructions, and responses.

**Branch Information Access:**

- **Complete Version of Messages**: `branch.messages_describe` offers a complete overview of the messages within the branch.
- **Branch Summary**: `branch.info()` provides a summary of the branch's conversational metrics and settings.
- **Last Instruction and Response**: Access the most recent instruction sent and the corresponding response with `branch.last_instruction` and `branch.last_response`.

```python
session = li.Session(system=system)
session.register_tools(tool_mul)

# Assume chat has been initiated and responses have been generated
branch = session.default_branch

# Access branch information
print(branch.messages_describe)
print(branch.info())
print("Last BaseInstruction:", branch.last_instruction)
print("Last Response:", branch.last_response)
```

### Filtering and Searching Branch Messages

LionAGI's branching functionality includes powerful message filtering and searching capabilities, enabling developers to query branch messages based on various criteria such as role, sender, time frame, and content keywords.

**Filtering and Searching Messages:**

- **Filter Messages**: `filter_messages_by` allows filtering messages based on role, sender, timestamps, and content keywords.
- **Search Keywords**: `search_keywords` helps find messages containing specific keywords.
- **Get Last Rows**: `get_last_rows` retrieves the last n messages from the branch, optionally filtered by sender or role.

```python
# Filter messages by assistant role containing the keyword 'output'
filtered_messages = branch.filter_messages_by(role='assistant', content_keywords='output')

# Search for messages containing the keyword 'task'
search_results = branch.search_keywords('task')

# Retrieve the last 3 messages
last_three_messages = branch.get_last_rows(n=3)
```

### Editing Branch Content

LionAGI allows for direct editing of branch content, including updating system messages, adding new messages, replacing keywords, rolling back changes, and extending the branch with additional messages.

**Editing Branch Messages:**

- **Change First System Message**: Modify the initial system message of the branch with `change_first_system_message`.
- **Add Message**: Insert a new message into the branch using `add_message`.
- **Replace Keyword**: Substitute a specific keyword within the branch messages using `replace_keyword`.
- **Rollback**: Revert the last n changes made to the branch with `rollback`.
- **Extend**: Append a DataFrame of messages to the branch using `extend`.

```python
# Update the first system message
branch.change_first_system_message(system='Updated System')

# Add a new instruction message
branch.add_message(instruction='A new instruction added')

# Replace 'function' with 'func' in branch messages
branch.replace_keyword('function', 'func')

# Rollback the last 4 changes
branch.rollback(4)

# Extend the branch with additional messages
branch.extend(df)  # Assuming df is a DataFrame of messages
```

### Conclusion

Through detailed branch info access, message filtering, and dynamic editing capabilities, LionAGI empowers developers to manage complex conversational flows with precision. These advanced branch management features facilitate the development of sophisticated AI-driven applications, enabling seamless integration of custom logic, detailed analysis of conversational data, and flexible adaptation of conversational strategies based on real-time insights.