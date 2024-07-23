from abc import ABC
from typing import Any, Optional

from lion_core.record.form import Form
from lion_core.communication.instruction import Instruction
from lion_core.validator.validator import Validator


class UnitChatMixin(ABC):
    """
    DirectiveMixin is a class for handling chat operations and
    processing responses.
    """

    def _create_chat_config(
        self,
        system: Optional[str] = None,
        instruction: Optional[str] = None,
        context: Optional[str] = None,
        images: Optional[str] = None,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
        requested_fields: Optional[list] = None,
        form: Form = None,
        tools: bool = False,
        branch: Optional[Any] = None,
        **kwargs,
    ) -> Any:
        """
        Create the chat configuration based on the provided parameters.

        Args:
            system: System message.
            instruction: Instruction message.
            context: Context message.
            sender: Sender identifier.
            recipient: Recipient identifier.
            requested_fields: Fields requested in the response.
            form: Form data.
            tools: Flag indicating if tools should be used.
            branch: Branch instance.
            kwargs: Additional keyword arguments.

        Returns:
            dict: The chat configuration.
        """
        branch = branch or self.branch

        if system:
            branch.add_message(system=system)

        if not form:
            if recipient == "branch.ln_id":
                recipient = branch.ln_id

            branch.add_message(
                instruction=instruction,
                context=context,
                sender=sender,
                recipient=recipient,
                requested_fields=requested_fields,
                images=images,
            )
        else:
            instruct_ = Instruction.from_form(form)
            branch.add_message(instruction=instruct_)

        if "tool_parsed" in kwargs:
            kwargs.pop("tool_parsed")
            tool_kwarg = {"tools": tools}
            kwargs = tool_kwarg | kwargs
        elif tools and branch.has_tools:
            kwargs = branch.tool_manager.parse_tool(tools=tools, **kwargs)

        config = {**self.imodel.config, **kwargs}
        if sender is not None:
            config["sender"] = sender

        return config

    async def _call_chatcompletion(
        self, imodel: Optional[Any] = None, branch: Optional[Any] = None, **kwargs
    ) -> Any:
        """
        Calls the chat completion model.

        Args:
            imodel: The model instance.
            branch: The branch instance.
            kwargs: Additional keyword arguments.

        Returns:
            Any: The chat completion result.
        """
        imodel = imodel or self.imodel
        branch = branch or self.branch
        return await imodel.call_chat_completion(branch.to_chat_messages(), **kwargs)

    async def _process_chatcompletion(
        self,
        payload: dict,
        completion: dict,
        sender: str,
        invoke_tool: bool = True,
        branch: Optional[Any] = None,
        action_request: Optional[Any] = None,
        costs=None,
    ) -> Any:
        """
        Processes the chat completion response.
        Currently only support last message for function calling

        Args:
            payload: The payload data.
            completion: The completion data.
            sender: The sender identifier.
            invoke_tool: Flag indicating if tools should be invoked.
            branch: The branch instance.
            action_request: The action request instance.

        Returns:
            Any: The processed result.
        """
        branch = branch or self.branch
        _msg = None

        if "choices" in completion:
            payload.pop("messages", None)
            branch.update_last_instruction_meta(payload)
            _choices = completion.pop("choices", None)

            def process_completion_choice(choice, price=None):
                if isinstance(choice, dict):
                    msg = choice.pop("message", None)
                    _completion = completion.copy()
                    _completion.update(choice)
                    branch.add_message(
                        assistant_response=msg,
                        metadata=_completion,
                        sender=sender,
                    )

                a = branch.messages[-1]._meta_get(
                    ["extra", "usage", "prompt_tokens"], 0
                )
                b = branch.messages[-1]._meta_get(
                    ["extra", "usage", "completion_tokens"], 0
                )
                m = completion.get("model", None)
                if m:
                    ttl = (a * price[0] + b * price[1]) / 1000000
                    branch.messages[-1]._meta_insert(["extra", "usage", "expense"], ttl)
                return msg

            if _choices and not isinstance(_choices, list):
                _choices = [_choices]

            if _choices and isinstance(_choices, list):
                for _choice in _choices:
                    _msg = process_completion_choice(_choice, price=costs)

            branch.imodel.status_tracker.num_tasks_succeeded += 1
        else:
            branch.imodel.status_tracker.num_tasks_failed += 1

        return await self._process_action_request(
            _msg=_msg,
            branch=branch,
            invoke_tool=invoke_tool,
            action_request=action_request,
        )

    async def _output(
        self,
        payload: dict,
        completion: dict,
        sender: str,
        invoke_tool: bool,
        requested_fields: dict,
        form: Form = None,
        return_form: bool = True,
        strict: bool = False,
        rulebook: Any = None,
        use_annotation: bool = True,
        template_name: str = None,
        costs=None,
    ) -> Any:
        """
        Outputs the final processed response.

        Args:
            payload: The payload data.
            completion: The completion data.
            sender: The sender identifier.
            invoke_tool: Flag indicating if tools should be invoked.
            requested_fields: Fields requested in the response.
            form: Form data.
            return_form: Flag indicating if form should be returned.
            strict: Flag indicating if strict validation should be applied.
            rulebook: Rulebook instance for validation.
            use_annotation: Flag indicating if annotations should be used.
            template_name: Template name for form.

        Returns:
            Any: The processed response.
        """
        _msg = await self._process_chatcompletion(
            payload=payload,
            completion=completion,
            sender=sender,
            invoke_tool=invoke_tool,
            costs=costs,
        )

        if _msg is None:
            return None

        response_ = self._process_model_response(_msg, requested_fields)

        if form:
            validator = Validator(rulebook=rulebook) if rulebook else self.validator
            form = await validator.validate_response(
                form=form,
                response=response_,
                strict=strict,
                use_annotation=use_annotation,
            )
            if template_name:
                form.template_name = template_name

            return (
                form
                if return_form
                else {
                    i: form.work_fields[i]
                    for i in form.requested_fields
                    if form.work_fields[i] is not None
                }
            )

        return response_

    async def _base_chat(
        self,
        instruction: Any = None,
        *,
        system: Any = None,
        context: Any = None,
        sender: Any = None,
        recipient: Any = None,
        requested_fields: dict = None,
        form: Form = None,
        tools: Any = False,
        images: Optional[str] = None,
        invoke_tool: bool = True,
        return_form: bool = True,
        strict: bool = False,
        rulebook: Any = None,
        imodel: Any = None,
        use_annotation: bool = True,
        branch: Any = None,
        clear_messages: bool = False,
        return_branch: bool = False,
        **kwargs,
    ) -> Any:
        """
        Handles the base chat operation by configuring the chat and
        processing the response.

        Args:
            instruction: Instruction message.
            system: System message.
            context: Context message.
            sender: Sender identifier.
            recipient: Recipient identifier.
            requested_fields: Fields requested in the response.
            form: Form data.
            tools: Flag indicating if tools should be used.
            invoke_tool: Flag indicating if tools should be invoked.
            return_form: Flag indicating if form should be returned.
            strict: Flag indicating if strict validation should be applied.
            rulebook: Rulebook instance for validation.
            imodel: Model instance.
            use_annotation: Flag indicating if annotations should be used.
            branch: Branch instance.
            clear_messages: Flag indicating if messages should be cleared.
            return_branch: Flag indicating if branch should be returned.
            kwargs: Additional keyword arguments.

        Returns:
            Any: The processed response and branch.
        """
        branch = branch or self.branch
        if clear_messages:
            branch.clear()
            branch.set_system(system)

        config = self._create_chat_config(
            system=system,
            instruction=instruction,
            context=context,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            branch=branch,
            images=images,
            **kwargs,
        )

        payload, completion = await self._call_chatcompletion(
            imodel=imodel, branch=branch, **config
        )

        imodel = imodel or self.imodel
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
            costs=imodel.costs,
        )

        return out_, branch if return_branch else out_

    async def _chat(
        self,
        instruction=None,
        context=None,
        system=None,
        sender=None,
        recipient=None,
        branch=None,
        requested_fields=None,
        form: Form = None,
        tools=False,
        invoke_tool=True,
        return_form=True,
        strict=False,
        rulebook=None,
        imodel=None,
        images: Optional[str] = None,
        clear_messages=False,
        use_annotation=True,
        timeout: float = None,
        return_branch=False,
        **kwargs,
    ):
        """
        Handles the chat operation.

        Args:
            instruction: Instruction message.
            context: Context message.
            system: System message.
            sender: Sender identifier.
            recipient: Recipient identifier.
            branch: Branch instance.
            requested_fields: Fields requested in the response.
            form: Form data.
            tools: Flag indicating if tools should be used.
            invoke_tool: Flag indicating if tools should be invoked.
            return_form: Flag indicating if form should be returned.
            strict: Flag indicating if strict validation should be applied.
            rulebook: Rulebook instance for validation.
            imodel: Model instance.
            clear_messages: Flag indicating if messages should be cleared.
            use_annotation: Flag indicating if annotations should be used.
            timeout: Timeout value.
            return_branch: Flag indicating if branch should be returned.
            kwargs: Additional keyword arguments.

        Returns:
            Any: The processed response.
        """
        a = await self._base_chat(
            context=context,
            instruction=instruction,
            system=system,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            images=images,
            invoke_tool=invoke_tool,
            return_form=return_form,
            strict=strict,
            rulebook=rulebook,
            imodel=imodel,
            use_annotation=use_annotation,
            timeout=timeout,
            branch=branch,
            clear_messages=clear_messages,
            return_branch=return_branch,
            **kwargs,
        )

        if isinstance(a, str):
            return a

        a = list(a)

        if len(a) == 2 and a[0] == a[1]:
            return a[0] if not isinstance(a[0], tuple) else a[0][0]
        if len(a) == 2 and a[0] != a[1]:
            return a[0], a[1]
        if len(a) == 1 and isinstance(a[0], tuple):
            return a[0][0]
        if len(a) == 1 and not isinstance(a[0], tuple):
            return a[0]
