from abc import ABC
from lionagi.libs.ln_convert import strip_lower


class DirectiveMixin(ABC):

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
        from lionagi.core.directive.chat import Chat

        directive = Chat(self, imodel=imodel, rulebook=rulebook)
        return await directive.chat(
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
            max_concurrency=max_concurrency,
            throttle_period=throttle_period,
            **kwargs,
        )

    async def direct(
        self,
        directive: str,  # examples, "chat", "predict", "act"
        instruction=None,  # additional instruction
        context=None,  # context to perform the instruction on
        **kwargs,
    ):

        from lionagi.core.directive._mapping import DIRECTIVE_MAPPING

        directive = strip_lower(directive)

        if directive not in DIRECTIVE_MAPPING:
            raise ValueError(f"Directive {directive} not found in DIRECTIVE_MAPPING")

        directive = DIRECTIVE_MAPPING[directive](self)

        return await directive.direct(
            context=context,
            instruction=instruction,
            **kwargs,
        )

    # default is chain of predict
    async def chain_of_direct(
        self,
        directive: str,
        instruction=None,  # additional instruction
        context=None,  # context to perform the instruction on
        **kwargs,
    ):

        from lionagi.core.directive.structure.chain import Chain

        _chain = Chain(self)

        return await _chain.chain(
            context=context,
            instruction=instruction,
            directive=directive,
            **kwargs,
        )
