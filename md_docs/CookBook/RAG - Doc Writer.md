## Tutorial: Using Lionagi to Handle API Documentation Generation

In this tutorial, we will demonstrate how to use the Lionagi package to generate API documentation for your code. We will walk through the steps of installing the package, preparing the data, chunking the data, embedding the chunks, and constructing a workflow to automate the documentation process. Below are the detailed steps along with code snippets to help you follow along.

### Step 1: Install Lionagi Package

First, we need to install the Lionagi package. This can be done using the `%pip install` command in a Jupyter notebook cell.

```python
%pip install lionagi
```

### Step 2: Import Lionagi

Next, we import the Lionagi package and set up the path to the data directory.

```python
import lionagi as li
from pathlib import Path

data_path = Path.cwd() / "lionagi_data"  # Path to the data directory
```

### Step 3: Prepare Data

We load the Python files from the specified directory into the `docs` variable. The files are filtered to include only those with content length greater than 100 characters.

```python
# Load files from directory
docs = li.load(input_dir=data_path, recursive=True, required_exts=[".py"])
docs = [doc for doc in docs if len(doc.content) > 100]
```

### Step 4: Chunk the Data

Commented out in this example are the steps to chunk the data. You can adjust the chunk size and overlap according to your needs. Then, the chunks can be embedded.

```python
# # chunk
# pile = li.chunk(docs=docs, chunk_size=2000, overlap=0.1)

# embed
# await pile.embed_pile()

# # save
# pile.to_csv("lionagi_embedding.csv")
```

### Step 5: Reload the Pile from Saved CSV

If you have previously saved the embeddings to a CSV file, you can reload them using the following command.

```python
# Reload pile from saved csv
pile = li.pile(csv_file="lionagi_embedding.csv")
```

### Step 6: Construct Workflow

Define the instruction for generating the API documentation. We use Lionagi's model and tools to construct a workflow that processes the instruction within the given context.

```python
instruction = """
write a good API documentation for this code, must use 
query engine to check meanings of related code concepts 
to accurately describe, for example if a name of a variable,
function, class, or module is used but not present in context,
you must check with the query engine. make sure to cross 
reference the code with the query engine to ensure the 
documentation is accurate.
"""

from PROMPTS import sys_prompt  # put your system prompt here

model = li.iModel(
    model="gpt-4o",
    provider="openai",
    interval_tokens=1_000_000,
    interval_requests=1_000,
    interval=60,
)

tools = pile.as_query_tool(
    name="qa_lionagi",
    guidance="Perform query to a QA bot",
    query_description="a term/phrase to lookup or a question to answer",
)
```

### Step 7: Execute the Instruction

We create a branch to handle the instruction and direct the process. The process involves generating the documentation using the model, querying necessary information, and integrating the responses.

```python
branch = li.Branch(system=sys_prompt, tools=tools, imodel=model)

form = await branch.direct(
    instruction=instruction,
    context=docs[83].content,
    allow_action=True,
    allow_extension=True,
    verbose=True,
    max_extensions=2,
    retries=3,  # sometimes the model may fail to generate a valid response or refuse to take actions
)
```

### Step 8: Display the Documentation

Finally, we display the generated API documentation.

```python
form.display()
```

By following these steps, you can automate the process of generating API documentation using the Lionagi package. This workflow allows you to efficiently handle documentation tasks, ensuring accuracy and completeness.