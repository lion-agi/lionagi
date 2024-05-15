from lionagi.libs.ln_func_call import rcall, CallDecorator as cd, Throttle
from .base import BaseDirective


class Chat(BaseDirective):

    async def chat(
        self,
        instruction=None,  # additional instruction
        context=None,  # context to perform the instruction on
        *,
        system=None,  # optionally swap system message
        sender=None,  # sender of the instruction, default "user"
        recipient=None,  # recipient of the instruction, default "branch.ln_id"
        branch=None,
        requested_fields=None,  # fields to request from the context, default None
        form=None,  # form to create instruction from, default None,
        tools=False,  # the tools to use, use True to consider all tools, no tools by default
        invoke_tool=True,  # whether to invoke the tool when function calling, default True
        return_form=True,  # whether to return the form if a form is passed in, otherwise return a dict/str
        strict=False,  # whether to strictly enforce the rule validation, default False
        rulebook=None,  # the rulebook to use for validation, default None, use default rulebook
        imodel=None,  # the optinally swappable iModel for the commands, otherwise self.branch.imodel
        clear_messages=False,
        use_annotation=True,  # whether to use annotation as rule qualifier, default True, (need rulebook if False)
        retries: int = 3,  # kwargs for rcall, number of retries if failed
        delay: float = 0,  # number of seconds to delay before retrying
        backoff_factor: float = 1,  # exponential backoff factor, default 1 (no backoff)
        default=None,  # default value to return if all retries failed
        timeout: (
            float | None
        ) = None,  # timeout for the rcall, default None (no timeout)
        timing: bool = False,  # if timing will return a tuple (output, duration)
        max_concurrency: int = 10_000,  # max concurrency for the chat, default 10_000 (global max concurrency)
        throttle_period: int = None,
        return_branch=False,
        **kwargs,
    ):

        @cd.max_concurrency(max_concurrency)
        async def _inner(**_kwargs):
            return await rcall(self._chat, **_kwargs)

        if throttle_period:
            throttle = Throttle(period=throttle_period)
            _inner = throttle(_inner)

        a = await _inner(
            context=context,
            instruction=instruction,
            system=system,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            invoke_tool=invoke_tool,
            return_form=return_form,
            strict=strict,
            rulebook=rulebook,
            imodel=imodel,
            use_annotation=use_annotation,
            retries=retries,
            delay=delay,
            backoff_factor=backoff_factor,
            default=default,
            timeout=timeout,
            timing=timing,
            branch=branch,
            clear_messages=clear_messages,
            return_branch=return_branch,
            **kwargs,
        )
        
        if isinstance(a, tuple) and isinstance(a[0], tuple):
            return a[0][0], a[1]
        if isinstance(a, tuple) and not isinstance(a[0], tuple):
            return a[0]
        

    async def _chat(
        self,
        instruction=None,
        *,
        system=None,
        context=None,
        sender=None,
        recipient=None,
        requested_fields=None,
        form=None,
        tools=False,
        invoke_tool=True,
        return_form=True,
        strict=False,
        rulebook=None,
        imodel=None,
        use_annotation=True,
        branch=None,
        clear_messages=False,
        return_branch=False,
        **kwargs,
    ):
        branch = branch or self.branch
        if clear_messages:
            branch.clear()

        config = self._create_chat_config(
            system=system,
            instruction=instruction,
            context=context,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            **kwargs,
        )

        payload, completion = await self._call_chatcompletion(
            imodel=imodel, branch=branch, **config
        )

        out_ = await self._output(
            payload=payload,
            completion=completion,
            sender=sender,
            invoke_tool=invoke_tool,
            requested_fields=requested_fields,
            form=form,
            return_form=return_form,
            strict=strict,
            rulebook=rulebook,
            use_annotation=use_annotation,
        )

        
        return out_, branch if return_branch else out_

    async def direct(self, *args, **kwargs):
        return await self.chat(*args, **kwargs)
