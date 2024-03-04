
Let us develop a dev bot that can

-   read and understand lionagi's existing codebase
-   QA with the codebase to clarify tasks
-   produce and tests pure python codes with code interpreter with
    automatic followup if quality is less than expected
-   output final runnable python codes

This tutorial shows you how you can automatically produce high quality
prototype and drafts codes customized for your own codebase.

To get started, make sure to install the necessary packages.

``` python
# %pip install lionagi llama_index pyautogen
```

Also, set up some parameters for future reference.

``` python
from pathlib import Path
import lionagi as li

# give a project name
project_name = "autodev_lion"

# extension of files of interest, can be str or list[str]
ext=".py"

# directory of source - lionagi codebase
data_dir = Path.cwd() / 'lionagi'

# output dir
output_dir = "data/log/coder/"
```

We are going to build a [LlamaIndex](https://www.llamaindex.ai/) [Query
Engine](https://docs.llamaindex.ai/en/stable/understanding/querying/querying.html)
for our codebase query.

``` python
from llama_index import SimpleDirectoryReader, ServiceContext, VectorStoreIndex
from llama_index.text_splitter import CodeSplitter
from llama_index.llms import OpenAI

splitter = CodeSplitter(
     language="python",
     chunk_lines=50,  # lines per chunk
     chunk_lines_overlap=10,  # lines overlap between chunks
     max_chars=1500,  # max chars per chunk
)

def get_query_engine(dir, splitter):
     documents = SimpleDirectoryReader(dir, required_exts=[ext], recursive=True).load_data()
     nodes = splitter.get_nodes_from_documents(documents)
     llm = OpenAI(temperature=0.1, model="gpt-4-1106-preview")
     service_context = ServiceContext.from_defaults(llm=llm)
     index1 = VectorStoreIndex(nodes, include_embeddings=True, service_context=service_context)
     query_engine = index1.as_query_engine(include_text=True, response_mode="tree_summarize")
     return query_engine

query_engine = get_query_engine(dir=data_dir, splitter=splitter)
```

Let\'s try to ask how session works and see what we get.

``` python
response = query_engine.query("Think step by step, explain how \
                               session works in details.")

from IPython.display import Markdown
Markdown(response.response)
```

![image](session_PE.png)

Next, we\'ll proceed to create an OAI assistant with code interpreter with [AutoGen](https://microsoft.github.io/autogen/).

To use AutoGen, you first need to download the [OAI_CONFIG_LIST_sample](https://github.com/microsoft/autogen/blob/main/OAI_CONFIG_LIST_sample).

Change your `api_key`, and rename the file as `OAI_CONFIG_LIST`, put in the same directory you are working in.


``` python
coder_instruction = f"""
     You are an expert at writing python codes. Write pure python codes, and
     run it to validate the codes, then return with the full implementation +
     the word TERMINATE when the task is solved and there is no problem. Reply
     FAILED if you cannot solve the problem.
     """
```

``` python
import autogen
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from autogen.agentchat import UserProxyAgent

config_list = autogen.config_list_from_json(
     "OAI_CONFIG_LIST",
     file_location=".",
     filter_dict={
         "model":
         ["gpt-3.5-turbo", "gpt-35-turbo", "gpt-4", "gpt4", "gpt-4-32k", "gpt-4-turbo"],
     },
)

# Initiate an agent equipped with code interpreter
gpt_assistant = GPTAssistantAgent(
     name="Coder Assistant",
     llm_config={
         "tools": [{"type": "code_interpreter"}],
         "config_list": config_list,
     },
     instructions = coder_instruction,
)

user_proxy = UserProxyAgent(
     name="user_proxy",
     is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
     code_execution_config={
         "work_dir": "coding",
         "use_docker": False,  # set to True or image name like "python:3" to use docker
     },
     human_input_mode="NEVER"
)

def code_pure_python(instruction):
     user_proxy.initiate_chat(gpt_assistant, message=instruction)
     return gpt_assistant.last_message()
```

With the query engine and the coder assistant configured and ready,
let\'s move on to crafting the tool description adhering to the OpenAI
schema.

``` python
tools = [{
         "type": "function",
         "function": {
             "name": "query_lionagi_codebase",
             "description": "Perform a query to a QA bot with access to a vector index built \
                             with package lionagi codebase",
             "parameters": {
                 "type": "object",
                 "properties": {
                     "str_or_query_bundle": {
                         "type": "string",
                         "description": "a question to ask the QA bot",
                     }
                 },
                 "required": ["str_or_query_bundle"],
             },
         }
     },
     {
         "type": "function",
         "function": {
             "name": "code_pure_python",
             "description": "Give an instruction to a coding assistant to write pure \
                             python codes",
             "parameters": {
                 "type": "object",
                 "properties": {
                     "instruction": {
                         "type": "string",
                         "description": "coding instruction to give to the coding assistant",
                     }
                 },
                 "required": ["instruction"],
             },
         }
     }
]

tool1 = li.Tool(func=query_engine.query, parser=lambda x: x.response, schema_=tools[0])
tool2 = li.Tool(func=code_pure_python, schema_=tools[1])
```

Let\'s craft prompts for solving coding tasks.

``` python
system = {
     "persona": "A helpful software engineer",
     "requirements": """
         Think step-by-step and provide thoughtful, clear, precise answers.
         Maintain a humble yet confident tone.
     """,
     "responsibilities": """
         Assist with coding in the lionagi Python package.
     """,
     "tools": """
         Use a QA bot for grounding responses and a coding assistant
         for writing pure Python code.
     """
}

function_call1 = {
     "notice": """
         Use the QA bot tool at least five times at each task step,
         identified by the step number. This bot can query source codes
         with natural language questions and provides natural language
         answers. Decide when to invoke function calls. You have to ask
         the bot for clarifications or additional information as needed,
         up to ten times if necessary.
     """
}

function_call2 = {
     "notice": """
         Use the coding assistant tool at least once at each task step,
         and again if a previous run failed. This assistant can write
         and run Python code in a sandbox environment, responding to
         natural language instructions with 'success' or 'failed'. Provide
         clear, detailed instructions for AI-based coding assistance.
     """
}

# Step 1: Understanding User Requirements
instruct1 = {
     "task_step": "1",
     "task_name": "Understand User Requirements",
     "task_objective": "Comprehend user-provided task fully",
     "task_description": """
         Analyze and understand the user's task. Develop plans
         for approach and delivery.
     """
 }

# Step 2: Proposing a Pure Python Solution
instruct2 = {
     "task_step": "2",
     "task_name": "Propose a Pure Python Solution",
     "task_objective": "Develop a detailed pure Python solution",
     "task_description": """
         Customize the coding task for lionagi package requirements.
         Use a QA bot for clarifications. Focus on functionalities
         and coding logic. Add lots more details here for
         more finetuned specifications
     """,
     "function_call": function_call1
}

# Step 3: Writing Pure Python Code
instruct3 = {
     "task_step": "3",
     "task_name": "Write Pure Python Code",
     "task_objective": "Give detailed instruction to a coding bot",
     "task_description": """
         Instruct the coding assistant to write executable Python code
         based on improved task understanding. Provide a complete,
         well-structured script if successful. If failed, rerun, report
         'Task failed' and the most recent code attempt after a second
         failure. Please notice that the coding assistant doesn't have
         any knowledge of the preceding conversation, please give as much
         details as possible when giving instruction. You cannot just
         say things like, as previously described. You must give detailed
         instruction such that a bot can write it
     """,
     "function_call": function_call2
}
```

With all instructions and tools set up, we can define our workflow now.

``` python
# solve a coding task in pure python
async def solve_in_python(context, num=4):

     # set up session and register both tools to session
     coder = li.Session(system, dir=output_dir)
     coder.register_tools([tool1, tool2])

     # initiate should not use tools
     await coder.initiate(instruct1, context=context, temperature=0.7)

      # auto_followup with QA bot tool
     await coder.auto_followup(instruct2, num=num, temperature=0.6, tools=[tools[0]])

      # auto_followup with code interpreter tool
     await coder.auto_followup(instruct3, num=2, temperature=0.5, tools=[tools[1]])

     # save to csv
     coder.messages_to_csv()
     coder.log_to_csv()

     # return codes
     return coder.conversation.messages[-1]['content']
```

How about tasking our developer with designing a File class and a Chunk
class for us?

``` python
issue = {
     "raise files and chunks into objects": """
         files and chunks are currently in dict format, please design classes for them, include all
         members, methods, staticmethods, class methods... if needed. please make sure your work
         has sufficient content, make sure to include typing and docstrings
     """
 }
```

``` python
response = await solve_in_python(issue)
```

``` python
from IPython.display import Markdown
import json

response = json.loads(response)
Markdown(response['output']['content'])
```

