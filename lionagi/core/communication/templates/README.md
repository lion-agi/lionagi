## Rendering Templates

Once templates are defined, you can load and render them using Jinja2:

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))

# Example: Rendering an instruction message
template = env.get_template('instruction_message.jinja2')
args = {
    "guidance": "Please ensure accuracy.",
    "instruction": "Summarize the document",
    "context": ["Doc1: ...", "Doc2: ..."],
    "request_fields": {"summary": "...", "key_points": "..."}
}
message_text = template.render(**args)
print(message_text)
```

Benefits and Customization
	•	You can easily rearrange sections within these templates without changing your code logic.
	•	Each message type is clearly separated, making it simpler to maintain or adjust one message format without affecting the others.
	•	If you find that you use some snippet (like rendering a schema) in multiple templates, you can factor it out into its own partial template (like tool_schemas.jinja2) and include it where needed.
	•	Over time, you can add more templates or split existing ones if certain messages become too complex.

By establishing this set of base templates and arguments, you have a starting point. You can expand or refine as your requirements evolve.
