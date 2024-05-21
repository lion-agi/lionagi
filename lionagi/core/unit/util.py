retry_kwargs = {
    "retries": 3,  # kwargs for rcall, number of retries if failed
    "delay": 0,  # number of seconds to delay before retrying
    "backoff_factor": 1,  # exponential backoff factor, default 1 (no backoff)
    "default": None,  # default value to return if all retries failed
    "timeout": None,  # timeout for the rcall, default None (no timeout)
    "timing": False,  # if timing will return a tuple (output, duration)
}

oai_fields = [
    "id",
    "object",
    "created",
    "model",
    "choices",
    "usage",
    "system_fingerprint",
]

choices_fields = ["index", "message", "logprobs", "finish_reason"]

usage_fields = ["prompt_tokens", "completion_tokens", "total_tokens"]

def process_tools(tool_obj, branch):
    if not isinstance(tool_obj, (list, tuple)):
        tool_obj = [tool_obj]
        
    tool_obj = [i for i in tool_obj if not isinstance(i, bool)]
    branch.tool_manager.update_tools(tool_obj)

async def _direct(
    directive,
    form=None,
    template=None,
    reason=False,
    confidence_score=None,
    instruction=None,
    context=None,
    template_kwargs={},
    **kwargs,
):
    if not form:
        form = template(
            instruction=instruction,
            context=context,
            confidence_score=confidence_score,
            reason=reason,
            **template_kwargs,
        )

    return await directive.direct(form=form, return_form=True, **kwargs)
