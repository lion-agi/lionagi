# lionagi/core/session/directive_mixin.py
from pydantic import BaseModel

from lionagi.core.unit import Unit

from ..message.action_response import ActionResponse


class DirectiveMixin:
    """
    Mixin class for handling chat interactions within the directive framework.
    """

    async def chat(
        self,
        instruction=None,  # additional instruction
        context=None,  # context to perform the instruction on
        system=None,  # optionally swap system message
        sender=None,  # sender of the instruction, default "user"
        recipient=None,  # recipient of the instruction, default "branch.ln_id"
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
        retries: int = 3,
        delay: float = 0,
        backoff_factor: float = 1,
        default=None,
        timeout: float = None,
        timing: bool = False,
        images=None,
        image_path=None,
        template=None,
        verbose=True,
        formatter=None,
        format_kwargs=None,
        pydantic_model: type[BaseModel] = None,
        return_pydantic_model: bool = False,
        **kwargs,
    ):
        """
        Asynchronously handles a chat interaction within the directive framework.

        This method processes an instruction with the given context and optional
        parameters, interacting with tools, models, and validation rules as needed.
        It manages retries, timeouts, concurrency, and can optionally clear
        previous messages, swap system messages, and control the use of
        annotations and rulebooks.

        Args:
            instruction (str, optional): Additional instruction to process.
            context (Any, optional): Context to perform the instruction on.
            system (str, optional): Optionally swap the system message.
            sender (str, optional): Sender of the instruction, default is "user".
            recipient (str, optional): Recipient of the instruction, default is
                "branch.ln_id".
            requested_fields (dict[str, str], optional): Fields to request from
                the context.
            form (Any, optional): Form to create instruction from, default is None.
            tools (bool, optional): Tools to use, use True to consider all tools,
                no tools by default.
            invoke_tool (bool, optional): Whether to invoke the tool when function
                calling, default is True.
            return_form (bool, optional): Whether to return the form if a form is
                passed in, otherwise return a dict/str.
            strict (bool, optional): Whether to strictly enforce rule validation,
                default is False.
            rulebook (Any, optional): The rulebook to use for validation, default
                is None (uses default rulebook).
            imodel (iModel, optional): Optionally swappable iModel for the
                commands, otherwise self.branch.imodel.
            clear_messages (bool, optional): Whether to clear previous messages,
                default is False.
            use_annotation (bool, optional): Whether to use annotation as rule
                qualifier, default is True (needs rulebook if False).
            retries (int, optional): Number of retries if failed, default is 3.
            delay (float, optional): Number of seconds to delay before retrying,
                default is 0.
            backoff_factor (float, optional): Exponential backoff factor, default
                is 1 (no backoff).
            default (Any, optional): Default value to return if all retries failed.
            timeout (float, optional): Timeout for the rcall, default is None
                (no timeout).
            timing (bool, optional): If True, will return a tuple (output,
                duration), default is False.
            return_branch (bool, optional): Whether to return the branch after
                processing, default is False.
            **kwargs: Additional keyword arguments for further customization.

        Returns:
            Any: The result of the chat processing, format determined by the
                `return_form` parameter.

        Raises:
            ValueError: If an invalid combination of parameters is provided.

        Examples:
            >>> result = await self.chat(instruction="Hello", context={"data": "example"})
            >>> print(result)
        """

        directive = Unit(
            self,
            imodel=imodel,
            rulebook=rulebook,
            template=template,
            verbose=verbose,
            formatter=formatter,
            format_kwargs=format_kwargs,
        )
        if system:
            self.add_message(system=system)

        if not images and image_path:
            from lionagi.libs import ImageUtil

            images = ImageUtil.read_image_to_base64(image_path)

        output = await directive.chat(
            instruction=instruction,
            context=context,
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
            clear_messages=clear_messages,
            images=images,
            return_pydantic_model=return_pydantic_model,
            pydantic_model=pydantic_model,
            return_branch=False,
            **kwargs,
        )
        if (
            isinstance(output, tuple | list)
            and len(output) == 2
            and output[0] == output[1]
        ):
            output = output[0]
        return output

    async def direct(
        self,
        *,
        instruction=None,
        context=None,
        form=None,
        tools=None,
        reason: bool = False,
        predict: bool = False,
        score=None,
        select=None,
        plan=None,
        allow_action: bool = False,
        allow_extension: bool = False,
        max_extension: int = None,
        confidence=None,
        score_num_digits=None,
        score_range=None,
        select_choices=None,
        plan_num_step=None,
        predict_num_sentences=None,
        imodel=None,
        system=None,
        rulebook=None,
        directive=None,
        images=None,
        image_path=None,
        template=None,
        verbose=True,
        formatter=None,
        format_kwargs=None,
        **kwargs,
    ):
        """
        Asynchronously directs the operation based on the provided parameters.

        Args:
            instruction (str, optional): Instruction message.
            context (Any, optional): Context to perform the instruction on.
            form (Form, optional): Form data.
            tools (Any, optional): Tools to use.
            reason (bool, optional): Flag indicating if reason should be included.
            predict (bool, optional): Flag indicating if prediction should be included.
            score (Any, optional): Score parameters.
            select (Any, optional): Select parameters.
            plan (Any, optional): Plan parameters.
            allow_action (bool, optional): Flag indicating if action should be allowed.
            allow_extension (bool, optional): Flag indicating if extension should be allowed.
            max_extension (int, optional): Maximum extension value.
            confidence (Any, optional): Confidence parameters.
            score_num_digits (int, optional): Number of digits for score.
            score_range (tuple, optional): Range for score.
            select_choices (list, optional): Choices for selection.
            plan_num_step (int, optional): Number of steps for plan.
            predict_num_sentences (int, optional): Number of sentences for prediction.
            imodel (iModel, optional): Optionally swappable iModel for the commands.
            system (str, optional): Optionally swap the system message.
            rulebook (Any, optional): The rulebook to use for validation.
            directive (str, optional): Directive for the operation.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The processed response.

        Examples:
            >>> result = await self.direct(instruction="Process data", context={"data": "example"})
            >>> print(result)
        """
        if system:
            self.add_message(system=system)

        if not images and image_path:
            from lionagi.libs import ImageUtil

            images = ImageUtil.read_image_to_base64(image_path)

        _directive = Unit(
            self,
            imodel=imodel,
            rulebook=rulebook,
            verbose=verbose,
            formatter=formatter,
            format_kwargs=format_kwargs,
        )

        idx = len(self.progress)
        if directive and isinstance(directive, str):
            form = await _directive.direct(
                directive=directive,
                instruction=instruction,
                context=context,
                tools=tools,
                reason=reason,
                confidence=confidence,
                images=images,
                template=template,
                **kwargs,
            )

            action_responses = [
                i for i in self.messages[idx:] if isinstance(i, ActionResponse)
            ]
            if len(action_responses) > 0:
                _dict = {
                    f"action_{idx}": i.content["action_response"]
                    for idx, i in enumerate(action_responses)
                }
                if not hasattr(form, "action_response"):
                    form.append_to_request("action_response", {})
                form.action_response.update(_dict)

            return form

        form = await _directive.direct(
            instruction=instruction,
            context=context,
            form=form,
            tools=tools,
            reason=reason,
            predict=predict,
            score=score,
            select=select,
            plan=plan,
            allow_action=allow_action,
            allow_extension=allow_extension,
            max_extension=max_extension,
            confidence=confidence,
            score_num_digits=score_num_digits,
            score_range=score_range,
            select_choices=select_choices,
            plan_num_step=plan_num_step,
            predict_num_sentences=predict_num_sentences,
            images=images,
            template=template,
            **kwargs,
        )

        action_responses = [
            i for i in self.messages[idx:] if isinstance(i, ActionResponse)
        ]
        if len(action_responses) > 0:
            _dict = {
                f"action_{idx}": i.content["action_response"]
                for idx, i in enumerate(action_responses)
            }
            if not hasattr(form, "action_response"):
                form.append_to_request("action_response", {})
            form.action_response.update(_dict)

        return form
