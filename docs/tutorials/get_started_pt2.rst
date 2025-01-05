.. _lionagi-get-started-part2:

====================================================
Get Started (Part 2): Using a Custom iModel
====================================================

In this second part of our **Get Started** tutorial, we'll explore how to:
 
1. **Set up a Branch** with a custom system prompt.
2. **Configure** an iModel from various providers (OpenAI, Anthropic, Perplexity).
3. **Send instructions** to produce typed outputs via Pydantic models.
4. **Review** the conversation and **demonstrate** the actual results.

We'll also **show the outputs** produced in a Python session so you know what to expect.

-----------------------------------
0. Prerequisites & Environment Setup
-----------------------------------

1. **lionagi**: Install or upgrade:

   .. code-block:: bash

      pip install lionagi

2. **Provider API Keys**:
   - **OpenAI**: get your key from https://openai.com.  
     Set it: ``export OPENAI_API_KEY='<YOUR_KEY>'``.
   - **Anthropic**: get your key from https://www.anthropic.com.  
     Set it: ``export ANTHROPIC_API_KEY='<YOUR_KEY>'``.
   - **Perplexity**: read https://docs.perplexity.ai/home to obtain a key.  
     Set it: ``export PERPLEXITY_API_KEY='<YOUR_KEY>'``.

3. A Python environment with an **async** runtime (e.g., Jupyter) or a 
   standard Python script using `asyncio`.

If you're new to **LionAGI**, see Part 1 for how to run a simple code-generation
task. In **Part 2**, we expand to multi-provider usage, with typed model outputs
via Pydantic.

--------------------------------------
1. Create a Branch & System Prompt
--------------------------------------
A **Branch** manages conversation messages, tools, and iModels. 
Below, we create a branch named “hunter,” giving it a **system** prompt 
so that any conversation with it follows certain style:

.. code-block:: python

   from lionagi import iModel, Branch

   system_prompt = (
       "You are a hilarious dragon hunter who responds in 10 words rhymes"
   )
   hunter = Branch(name="hunter", system=system_prompt)

If you want the branch to incorporate memory or logs from previous steps,
just keep using the same ``hunter`` instance.


------------------------------------------
2. Using OpenAI GPT as a Custom iModel
------------------------------------------
We define an **iModel** referencing OpenAI's endpoints. 
For example, we specify a hypothetical “gpt-4o” model:

.. code-block:: python

   from lionagi import iModel

   gpt4o = iModel(
       provider="openai",
       task="chat",    # 'chat' or 'chat/completions'
       model="gpt-4o",
       # We assume your environment variable is OPENAI_API_KEY
   )

Then we call the branch's :meth:`communicate(...)` method, specifying
``imodel=gpt4o``:

.. code-block:: python

   a = await hunter.communicate(
       instruction="I am a dragon",
       imodel=gpt4o
   )
   print(a)

**Expected Output** (example; actual responses will vary):

.. code-block:: text

   Hello, ferocious beast of scales,
   Let me share comedic tales.

   # This is just an illustration of a "10 words rhyme" style, in practice
   # GPT's output might differ.

-------------------------------------------
3. Structured Output via Pydantic Model
-------------------------------------------
We can parse the model's response into a typed **Pydantic** model:

.. code-block:: python

   from pydantic import BaseModel

   class Joke(BaseModel):
       joke: str

   b = await hunter.communicate(
       instruction="I am a dragon",
       imodel=gpt4o,
       response_format=Joke,  # parse the LLM response into 'Joke'
   )

   print(type(b))
   print(b)

**Example Output**:

.. code-block:: text

   <class '__main__.Joke'>
   Joke(joke="Why do dragons never get the flu? They always keep it hot!")


------------------------------------------------------
4. Using Anthropic's “Claude” with a Different Model
------------------------------------------------------
We can define an iModel referencing Anthropic (e.g., a “claude-3-5-sonnet-20241022”).
Anthropic typically requires specifying a `max_tokens` field:

.. code-block:: python

   sonnet = iModel(
       provider="anthropic",
       model="claude-3-5-sonnet-20241022",
       max_tokens=1000,  # anthro requirement
   )

Now let's request the same Pydantic `Joke` output from it:

.. code-block:: python

   c = await hunter.communicate(
       instruction="I am a dragon",
       response_format=Joke,
       clear_messages=True,  # clear old conversation
       imodel=sonnet,
   )
   print(c)

**Possible Output**:

.. code-block:: text

   Joke(joke="Why did the dragon cross the road?
   Because wizard spells can't hold it aboad!")


-------------------------------------------------
5. Perplexity for “Internet-Search” or Q&A
-------------------------------------------------
**Perplexity** is another provider. We can define an iModel if you have
the correct plan & key:

.. code-block:: python

   pplx_small = iModel(
       provider="perplexity",
       task="chat/completions",
       model="llama-3.1-sonar-small-128k-online",
       max_tokens=1000,
   )

   b = await hunter.communicate(
       instruction="What makes a well-behaved dragon?",
       clear_messages=True,
       imodel=pplx_small,
   )
   print(b)

**Sample Output**:

.. code-block:: text

   A well-behaved dragon is polite, breathes no flame
   And helps lost travelers in all-lovely domain,
   No stolen gold, no hostage knights remain,
   Tame-lizard style is how they keep their fame.

   # Also might contain references or citations if Perplexity returns them.

---------------------------------------
6. Checking the Conversation Messages
---------------------------------------
Every request we do is tracked in the branch as messages. We can see them:

.. code-block:: python

   from lionagi import types

   for msg in hunter.messages:
       if msg.role == types.MessageRole.SYSTEM:
           print("System Prompt ->", msg.rendered)
       elif msg.role == types.MessageRole.USER:
           print("User Prompt ->", msg.rendered)
       elif msg.role == types.MessageRole.ASSISTANT:
           print("Assistant Output ->", msg.rendered)

We can also check low-level provider info:

.. code-block:: python

   # Last raw response from the model
   raw = hunter.msgs.last_response.model_response
   print(raw)


----------------------------------------------
7. Putting It All Together (Demonstration)
----------------------------------------------
Below is a **complete snippet** that sets up a branch, tries three providers,
and shows the typed “Joke” result. We also print out the conversation messages.


.. code-block:: python

   from lionagi import iModel, Branch, types
   from pydantic import BaseModel

   class Joke(BaseModel):
       joke: str

   # 1) Create the branch
   system_prompt = "You are a hilarious dragon hunter who responds in 10 words rhymes"
   hunter = Branch(name="hunter", system=system_prompt)

   # 2) OpenAI model
   gpt4o = iModel(provider="openai", model="gpt-4o")

   # 3) Communicate with structured output
   joke_res = await hunter.communicate(
       instruction="I am a dragon, amuse me",
       imodel=gpt4o,
       response_format=Joke
   )
   print("OpenAI Joke =>", joke_res)

   # 4) Anthropic model
   sonnet = iModel(provider="anthropic", model="claude-3-5-sonnet-20241022", max_tokens=1000)
   c = await hunter.communicate(
       instruction="Another comedic idea, short!",
       imodel=sonnet,
       response_format=Joke,
       clear_messages=True
   )
   print("Anthropic Joke =>", c)

   # 5) Print all messages in the conversation
   for msg in hunter.messages:
       print(msg.role, "=>", msg.rendered)

**Potential Output**:

.. code-block:: text

   OpenAI Joke => Joke(joke="How do dragons fix a leak? They use a scale!")
   Anthropic Joke => Joke(joke="When a dragon tries knitting, does it purl fiery threads?")
   system => You are a hilarious dragon hunter who responds in 10 words rhymes
   user => I am a dragon, amuse me
   assistant => ...
   user => Another comedic idea, short!
   assistant => ...

In practice, the actual text depends on your model usage, tokens, etc.


-----------
Next Steps
-----------
Now you've seen how to:

1. **Setup** multiple iModels in a single session.
2. **Communicate** with each to produce typed outputs.
3. **Inspect** messages for logs or debugging.

You can extend this approach for more advanced tasks—**agentic RAG** flows,
**embedding-based** retrieval, or hooking up advanced concurrency managers to
**queue** these calls.

**End of Part 2**. Keep exploring or see more advanced tutorials for hooking
**LionAGI** with concurrency and tool-based expansions!
