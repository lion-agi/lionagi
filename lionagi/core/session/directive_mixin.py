class DirectiveMixin:

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
        form=None,  # form to create instruction from, default None
        tools=False,  # the tools to use, use True to consider all tools, no tools by default
        invoke_tool=True,  # whether to invoke the tool when function calling, default True
        return_form=True,  # whether to return the form if a form is passed in, otherwise return a dict/str
        strict=False,  # whether to strictly enforce the rule validation, default False
        rulebook=None,  # the rulebook to use for validation, default None, use default rulebook
        imodel=None,  # the optionally swappable iModel for the commands, otherwise self.branch.imodel
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
        """
        Asynchronously handles a chat interaction within the directive framework.

        This method processes an instruction with the given context and optional parameters,
        interacting with tools, models, and validation rules as needed. It manages retries,
        timeouts, concurrency, and can optionally clear previous messages, swap system messages,
        and control the use of annotations and rulebooks.

        Args:
            instruction (str, optional): Additional instruction to process.
            context (Any, optional): Context to perform the instruction on.
            system (str, optional): Optionally swap the system message.
            sender (str, optional): Sender of the instruction, default is "user".
            recipient (str, optional): Recipient of the instruction, default is "branch.ln_id".
            branch (Branch, optional): The branch to use for the instruction.
            requested_fields (dict[str, str], optional): Fields to request from the context.
            form (Any, optional): Form to create instruction from, default is None.
            tools (bool, optional): Tools to use, use True to consider all tools, no tools by default.
            invoke_tool (bool, optional): Whether to invoke the tool when function calling, default is True.
            return_form (bool, optional): Whether to return the form if a form is passed in, otherwise return a dict/str.
            strict (bool, optional): Whether to strictly enforce rule validation, default is False.
            rulebook (Any, optional): The rulebook to use for validation, default is None (uses default rulebook).
            imodel (iModel, optional): Optionally swappable iModel for the commands, otherwise self.branch.imodel.
            clear_messages (bool, optional): Whether to clear previous messages, default is False.
            use_annotation (bool, optional): Whether to use annotation as rule qualifier, default is True (needs rulebook if False).
            retries (int, optional): Number of retries if failed, default is 3.
            delay (float, optional): Number of seconds to delay before retrying, default is 0.
            backoff_factor (float, optional): Exponential backoff factor, default is 1 (no backoff).
            default (Any, optional): Default value to return if all retries failed.
            timeout (float, optional): Timeout for the rcall, default is None (no timeout).
            timing (bool, optional): If True, will return a tuple (output, duration), default is False.
            max_concurrency (int, optional): Max concurrency for the chat, default is 10_000 (global max concurrency).
            throttle_period (int, optional): Throttle period for limiting execution, default is None.
            return_branch (bool, optional): Whether to return the branch after processing, default is False.
            **kwargs: Additional keyword arguments for further customization.

        Returns:
            Any: The result of the chat processing, format determined by the `return_form` parameter.

        Raises:
            ValueError: If an invalid combination of parameters is provided.

        Examples:
            >>> result = await self.chat(instruction="Hello", context={"data": "example"})
            >>> print(result)
        """
        from lionagi.core.directive.unit.unit import Unit

        directive = Unit(self, imodel=imodel, rulebook=rulebook)
        if system:
            self.add_message(system=system)

        return await directive.chat(
            context=context,
            instruction=instruction,
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

    # async def direct(
    #     self,
    #     directive: str,  # examples, "chat", "predict", "act"
    #     instruction=None,  # additional instruction
    #     context=None,  # context to perform the instruction on
    #     return_branch=False,
    #     **kwargs,
    # ):

    #     import lionagi.core.directive.direct as _direct

    #     directive = getattr(_direct, strip_lower(directive))

    #     output = await directive(
    #         context=context,
    #         instruction=instruction,
    #         return_branch=return_branch,
    #         **kwargs,
    #     )
    #     return output

    # _out = []
    # for item in list(output):
    #     if item not in _out:
    #         _out.append(item)

    # if not return_branch:
    #     return _out[0]
    # return _out

    # # default is chain of predict
    # async def chain_of_direct(
    #     self,
    #     directive: str,
    #     instruction=None,  # additional instruction
    #     context=None,  # context to perform the instruction on
    #     **kwargs,
    # ):

    #     from lionagi.core.directive.structure.chain import Chain

    #     _chain = Chain(self)

    #     return await _chain.direct(
    #         context=context,
    #         instruction=instruction,
    #         directive=directive,
    #         **kwargs,
    #     )
