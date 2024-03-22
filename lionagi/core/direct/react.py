from ..branch import Branch
from ..flow.monoflow import MonoReAct


async def react(
    instruction=None,
    system=None,
    context=None,
    output_fields=None,
    tools=None,
    reason_prompt=None,
    action_prompt=None,
    output_prompt=None,
    **kwargs,
):
    branch = Branch(system=system, tools=tools)
    flow = MonoReAct(branch)

    out = await flow._react(
        instruction=instruction,
        context=context,
        output_fields=output_fields,
        reason_prompt=reason_prompt,
        action_prompt=action_prompt,
        **kwargs,
    )

    output_prompt = output_prompt or "integrate everything, present final output"
    output_fields_ = {"answer": "..."}
    out1 = await flow.chat(output_prompt, output_fields=output_fields_)

    out["answer"] = out1["answer"]
    return out
