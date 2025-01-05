.. _lionagi-get-started-part3:

==========================================================
Get Started (Part 3): ``operate`` and Brainstorm
==========================================================

In this third installment of **Get Started** with LionAGI, we will:

1. Demonstrate the **operate** method for advanced instruction handling, including structured output, reasoning fields, and optional tool calls.

2. Show how to perform **brainstorm** operations that generate multiple sub-ideas, optionally auto-run or explore them, and then gather the results.


-------------------------
0. Prerequisites & Recap
-------------------------

- See **Part 1** (basic code generation) and **Part 2** (custom iModels, typed outputs) for initial setup.
- **Python 3.10+** is required for async usage.
- Install or set up your environment with LionAGI:
  
  .. code-block:: bash

     pip install lionagi

  (Also ensure any provider keys—like OpenAI or Anthropic—are set via environment variables if needed.)

------------------------------------
1. Using ``operate`` for Summaries
------------------------------------
``operate`` merges conversation (“chat” with an LLM) **and** potential tool invocation. 
You can parse the final output into a structured Pydantic model, include a ``reason`` field for the LLM's explanation, or let it call tools to refine data.

**Scenario**: Summarize some text and optionally call a named-entity tool if needed.

.. code-block:: python

   from IPython.display import display, Markdown
   from pydantic import BaseModel, Field
   from lionagi import types, Branch
   from lionagi.libs.parse import as_readable

   # 1) Define a data model for final output
   class SummModel(BaseModel):
       summary: str = Field(..., title="Summary of Input Text")

   # 2) A trivial tool to extract 'Location' entities from text
   def entity_extractor(text: str) -> list[str]:
       """
       Very naive entity extraction: finds words capitalized in the text
       (just for demo).
       """
       # Example: we split on whitespace, pick capitalized words
       words = text.split()
       return [w for w in words if w and w[0].isupper()]

   # 3) The function that uses Branch and .operate
   async def summarize_text(text: str):
       # Create Branch, register the entity_extractor as a tool
       branch = Branch(tools=entity_extractor)

       # Call branch.operate
       # instruction: we want the LLM to produce a summary, 
       # optionally calling the 'entity_extractor' tool if it needs to check location names, etc.
       # reason=True => store a 'reason' field in final output if model structure allows it
       # actions=True => allow tool usage
       # response_format=SummModel => parse final JSON back into SummModel
       result_model = await branch.operate(
           instruction="Summarize the following text. If you need to validate location entities, call 'entity_extractor'.",
           context={"text": text},
           response_format=SummModel,
           reason=True,
           actions=True,
       )

       # Present final results
       display(Markdown("## Final Summary"))
       display(Markdown(f"**Summary:** {result_model.summary}"))

       # If reason was present, show it in a nice format
       if hasattr(result_model, "reason"):
           display(Markdown("## Reasoning"))
           display(Markdown(as_readable(result_model.reason, md=True)))

       # Print out messages or actions for debugging
       for msg in branch.messages:
           if isinstance(msg, types.ActionResponse):
               display(Markdown("### Tool Invocation"))
               display(Markdown(as_readable(msg.content, md=True)))
           elif not isinstance(msg, types.ActionRequest):
               display(Markdown(f"### Message:\n{msg.rendered}"))

       return result_model

   # 4) Example usage
   text_to_summarize = (
       "Last week, Alice traveled to Paris to attend a tech conference. "
       "She visited the Louvre, met local developers, and discussed new AI trends."
   )

   final_summary = await summarize_text(text_to_summarize)
   print("Model Dump =>", final_summary.model_dump())

**Explanation**:
- We define a **SummModel** with a single field: ``summary``.
- The LLM can optionally call the ``entity_extractor`` tool if it needs  to confirm location references in the text.  
- We request a reasoning field (``reason=True``) so the final JSON can contain a short explanation or confidence measure.

**Sample Flow**:
- The LLM reads the instruction + text context, possibly calls the tool 
  for location checking, then returns a structured JSON with the summarizing text in ``summary`` (and an optional ``reason`` object if the LLM provides it).

-------------------------------------------------
2. Brainstorm: Generating & Exploring Ideas
-------------------------------------------------
**Brainstorm** is a multi-step approach:

1. Generate an initial set of sub-instructions (like topic expansions or tasks).
2. (Optional) **auto_run** each sub-instruction, collecting outputs.
3. (Optional) “explore” those results in a concurrency strategy (e.g., concurrent, sequential, or chunked).

**Usage**:

.. code-block:: python

   from IPython.display import display, Markdown
   from lionagi.operations import brainstorm
   from lionagi.libs.parse import as_readable
   from pydantic import BaseModel

   # a typed model for each sub-instruction
   class IdeaModel(BaseModel):
       idea: str
       rationale: str | None = None

   # We define the main instruct
   instruct_data = {
       "instruction": "Brainstorm 3 short ways to improve summarization tasks",
       "context": "Focus on large text corpora, potential tool usage, concurrency approaches"
   }

   result = await brainstorm(
       instruct=instruct_data,
       num_instruct=3,
       response_format=IdeaModel,
       auto_run=True,
       auto_explore=True,
       explore_strategy="concurrent", 
       reason=True,  # optionally get reason
       verbose=True
   )

   display(Markdown("## Brainstorm Initial"))
   display(Markdown(as_readable(result.initial, md=True)))

   if result.brainstorm:
       display(Markdown("## Brainstorm Sub-Results"))
       for br in result.brainstorm:
           display(Markdown(as_readable(br, md=True)))

   if result.explore:
       display(Markdown("## Further Explorations"))
       for ex in result.explore:
           display(Markdown("### Sub-Instruct"))
           display(Markdown(as_readable(ex.instruct, md=True)))
           display(Markdown("#### Model Response"))
           display(Markdown(ex.response))

**Key Points**:

- ``auto_run=True`` => we automatically run sub-instructions returned by the LLM.

- ``auto_explore=True`` => we also do a follow-up exploration pass with the chosen strategy.
- Each sub-instruction can produce typed results (like IdeaModel).

- The final **result** is a **BrainstormOperation** with fields: 

  - ``initial``: The first pass typed model
  - ``brainstorm``: The auto-run sub-instruction results
  - ``explore``: The expansions from exploring them further

--------------------------------
Conclusion & Next Steps
--------------------------------
- We showcased **``operate``** with structured output, reasoning fields,  and optional tool usage (like a naive entity extractor).
- We introduced **``brainstorm``** for multi-idea generation, auto-run,  and expansions.
- Combine these for real agentic workflows, multi-step reasoning,  or advanced concurrency. For deeper concurrency or multi-agent setups,  explore the advanced sections in the docs. 

**Happy experimenting** with LionAGI's flexible “operate” 
and “brainstorm” capabilities!
