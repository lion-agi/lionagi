import asyncio
import contextlib
import re
from abc import ABC
from typing import Any

from lionfuncs import extract_block, to_dict, validate_mapping

from lionagi.core.collections.abc import ActionError
from lionagi.core.message import ActionRequest, ActionResponse, Instruction
from lionagi.core.message.util import _parse_action_request
from lionagi.core.report.form import Form
from lionagi.core.unit.util import process_tools
from lionagi.libs.ln_nested import nmerge


class DirectiveMixin(ABC):
    """
    DirectiveMixin is a class for handling chat operations and
    processing responses.
    """

    def _create_chat_config(
        self,
        system: str | None = None,
        instruction: str | None = None,
        context: str | None = None,
        images: str | None = None,
        sender: str | None = None,
        recipient: str | None = None,
        requested_fields: list | None = None,
        form: Form = None,
        tools: bool = False,
        branch: Any | None = None,
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
        self, imodel: Any | None = None, branch: Any | None = None, **kwargs
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
        return await imodel.call_chat_completion(
            branch.to_chat_messages(), **kwargs
        )

    async def _process_chatcompletion(
        self,
        payload: dict,
        completion: dict,
        sender: str,
        invoke_tool: bool = True,
        branch: Any | None = None,
        action_request: Any | None = None,
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
                    branch.messages[-1]._meta_insert(
                        ["extra", "usage", "expense"], ttl
                    )
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

    async def _process_action_request(
        self,
        _msg: dict | None = None,
        branch: Any | None = None,
        invoke_tool: bool = True,
        action_request: Any | None = None,
    ) -> Any:
        """
        Processes an action request from the assistant response.

        Args:
            _msg: The message data.
            branch: The branch instance.
            invoke_tool: Flag indicating if tools should be invoked.
            action_request: The action request instance.

        Returns:
            Any: The processed result.
        """
        action_request = action_request or _parse_action_request(_msg)
        if action_request is None:
            return _msg if _msg else False

        if action_request:
            for i in action_request:
                if i.function in branch.tool_manager.registry:
                    i.recipient = branch.tool_manager.registry[
                        i.function
                    ].ln_id
                else:
                    raise ActionError(
                        f"Tool {i.function} not found in registry"
                    )
                branch.add_message(action_request=i, recipient=i.recipient)

        if invoke_tool:
            tasks = []
            for i in action_request:
                tool = branch.tool_manager.registry[i.function]
                tasks.append(asyncio.create_task(tool.invoke(i.arguments)))
            results = await asyncio.gather(*tasks)

            for idx, item in enumerate(results):
                if item is not None:
                    branch.add_message(
                        action_request=action_request[idx],
                        func_outputs=item,
                        sender=action_request[idx].recipient,
                        recipient=action_request[idx].sender,
                    )

        return None

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
            form = await self.validator.validate_response(
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
        images: str | None = None,
        invoke_tool: bool = True,
        return_form: bool = True,
        strict: bool = False,
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
            use_annotation=use_annotation,
            costs=imodel.costs or (0, 0),
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
        imodel=None,
        images: str | None = None,
        clear_messages=False,
        use_annotation=True,
        timeout: float = None,
        return_branch=False,
        formatter=None,
        format_kwargs={},
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
            imodel=imodel,
            use_annotation=use_annotation,
            timeout=timeout,
            branch=branch,
            clear_messages=clear_messages,
            return_branch=return_branch,
            formatter=formatter,
            format_kwargs=format_kwargs,
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

    async def _direct(
        self,
        instruction=None,
        context=None,
        form: Form = None,
        branch=None,
        tools=None,
        reason: bool = None,
        predict: bool = None,
        score: bool = None,
        select: bool = None,
        plan: bool = None,
        allow_action: bool = None,
        allow_extension: bool = None,
        confidence: bool = None,
        max_extension: int = None,
        score_num_digits=None,
        score_range=None,
        select_choices=None,
        plan_num_step=None,
        predict_num_sentences=None,
        clear_messages=False,
        return_branch=False,
        images: str | None = None,
        verbose=None,
        **kwargs,
    ):
        """
        Directs the operation based on the provided parameters.

        Args:
            instruction: Instruction message.
            context: Context message.
            form: Form data.
            branch: Branch instance.
            tools: Tools data.
            reason: Flag indicating if reason should be included.
            predict: Flag indicating if prediction should be included.
            score: Flag indicating if score should be included.
            select: Flag indicating if selection should be included.
            plan: Flag indicating if plan should be included.
            allow_action: Flag indicating if action should be allowed.
            allow_extension: Flag indicating if extension should be allowed.
            confidence: Flag indicating if confidence should be included.
            max_extension: Maximum extension value.
            score_num_digits: Number of digits for score.
            score_range: Range for score.
            select_choices: Choices for selection.
            plan_num_step: Number of steps for plan.
            predict_num_sentences: Number of sentences for prediction.
            clear_messages: Flag indicating if messages should be cleared.
            return_branch: Flag indicating if branch should be returned.
            kwargs: Additional keyword arguments.

        Returns:
            Any: The processed response and branch.
        """
        a = await self._base_direct(
            instruction=instruction,
            context=context,
            form=form,
            branch=branch,
            tools=tools,
            reason=reason,
            predict=predict,
            score=score,
            select=select,
            images=images,
            plan=plan,
            allow_action=allow_action,
            allow_extension=allow_extension,
            confidence=confidence,
            max_extension=max_extension,
            score_num_digits=score_num_digits,
            score_range=score_range,
            select_choices=select_choices,
            plan_num_step=plan_num_step,
            predict_num_sentences=predict_num_sentences,
            clear_messages=clear_messages,
            return_branch=return_branch,
            verbose=verbose,
            **kwargs,
        )

        a = list(a)
        if len(a) == 2 and a[0] == a[1]:
            return a[0] if not isinstance(a[0], tuple) else a[0][0]

        return a[0], a[1]

    async def _base_direct(
        self,
        instruction=None,
        *,
        context=None,
        form: Form = None,
        branch=None,
        tools=None,
        reason: bool = None,
        predict: bool = None,
        score: bool = None,
        select: bool = None,
        plan: bool = None,
        allow_action: bool = None,
        allow_extension: bool = None,
        confidence: bool = None,
        max_extension: int = None,
        score_num_digits=None,
        score_range=None,
        select_choices=None,
        plan_num_step=None,
        predict_num_sentences=None,
        clear_messages=False,
        return_branch=False,
        images: str | None = None,
        verbose=True,
        formatter=None,
        format_kwargs=None,
        **kwargs,
    ):
        """
        Handles the base direct operation.

        Args:
            instruction: Instruction message.
            context: Context message.
            form: Form data.
            branch: Branch instance.
            tools: Tools data.
            reason: Flag indicating if reason should be included.
            predict: Flag indicating if prediction should be included.
            score: Flag indicating if score should be included.
            select: Flag indicating if selection should be included.
            plan: Flag indicating if plan should be included.
            allow_action: Flag indicating if action should be allowed.
            allow_extension: Flag indicating if extension should be allowed.
            confidence: Flag indicating if confidence should be included.
            max_extension: Maximum extension value.
            score_num_digits: Number of digits for score.
            score_range: Range for score.
            select_choices: Choices for selection.
            plan_num_step: Number of steps for plan.
            predict_num_sentences: Number of sentences for prediction.
            clear_messages: Flag indicating if messages should be cleared.
            return_branch: Flag indicating if branch should be returned.
            kwargs: Additional keyword arguments.

        Returns:
            Any: The processed response and branch.
        """
        # Ensure branch is initialized
        branch = branch or self.branch
        if clear_messages:
            branch.clear()

        # Set a default max_extension if allow_extension is True and max_extension is None
        if allow_extension and not max_extension:
            max_extension = 3  # Set a default limit for recursion

        # Process tools if provided
        if tools:
            process_tools(tools, branch)

        if allow_action and not tools:
            tools = True

        tool_schema = None
        if tools:
            tool_schema = branch.tool_manager.get_tool_schema(tools)

        if not form:
            form = self.default_template(
                instruction=instruction,
                context=context,
                reason=reason,
                predict=predict,
                score=score,
                select=select,
                plan=plan,
                tool_schema=tool_schema,
                allow_action=allow_action,
                allow_extension=allow_extension,
                max_extension=max_extension,
                confidence=confidence,
                score_num_digits=score_num_digits,
                score_range=score_range,
                select_choices=select_choices,
                plan_num_step=plan_num_step,
                predict_num_sentences=predict_num_sentences,
            )

        elif form and "tool_schema" not in form._all_fields:
            form.append_to_input("tool_schema")
            form.tool_schema = tool_schema

        else:
            form.tool_schema = tool_schema

        verbose = (
            verbose
            if verbose is not None and isinstance(verbose, bool)
            else self.verbose
        )
        if verbose:
            print("Chatting with model...")

        # Call the base chat method
        form = await self._chat(
            form=form,
            branch=branch,
            images=images,
            **kwargs,
        )

        # Handle actions if allowed and required
        if allow_action and getattr(form, "action_required", None):
            actions = getattr(form, "actions", None)
            if actions:
                if verbose:
                    print(
                        "Found action requests in model response. Processing actions..."
                    )
                form = await self._act(form, branch, actions=actions)
                if verbose:
                    print("Actions processed!")

        last_form = form

        ctr = 1

        # Handle extensions if allowed and required
        extension_forms = []
        max_extension = max_extension if isinstance(max_extension, int) else 3
        while (
            allow_extension
            and max_extension > 0
            and getattr(last_form, "extension_required", None)
        ):
            if getattr(last_form, "is_extension", None):
                break
            if verbose:
                print(f"\nFound extension requests in model response.")
                print(
                    f"------------------- Processing extension No.{ctr} -------------------"
                )

            max_extension -= 1

            # new form cannot be extended, otherwise it will be an infinite loop
            new_form = await self._extend(
                tools=tools,
                reason=reason,
                predict=predict,
                score=score,
                select=select,
                plan=getattr(last_form, "plan", None),
                allow_action=allow_action,
                confidence=confidence,
                score_num_digits=score_num_digits,
                score_range=score_range,
                select_choices=select_choices,
                predict_num_sentences=predict_num_sentences,
                **kwargs,
            )

            if verbose:
                print(
                    f"------------------- Extension completed -------------------\n"
                )

            extension_forms.extend(new_form)
            last_form = (
                new_form[-1] if isinstance(new_form, list) else new_form
            )
            ctr += len(form)

        if extension_forms:
            if not getattr(form, "extension_forms", None):
                form._add_field("extension_forms", list, None, [])
            form.extension_forms.extend(extension_forms)
            action_responses = [
                i.action_response
                for i in extension_forms
                if getattr(i, "action_response", None) is not None
            ]
            if not hasattr(form, "action_response"):
                form.add_field("action_response", {})

            for action_response in action_responses:
                nmerge([form.action_response, action_response])

        if "PLEASE_ACTION" in form.answer:
            if verbose:
                print("Analyzing action responses and generating answer...")

            answer = await self._chat(
                "please provide final answer basing on the above"
                " information, provide answer value as a string only"
                " do not return as json, do not include other information",
            )

            if isinstance(answer, dict):
                a = answer.get("answer", None)
                if a is not None:
                    answer = a

            answer = str(answer).strip()
            if answer.startswith("{") and answer.endswith("}"):
                answer = answer[1:-1]
                answer = answer.strip()
            if '"answer":' in answer:
                answer.replace('"answer":', "")
                answer = answer.strip()
            elif "'answer':" in answer:
                answer.replace("'answer':", "")
                answer = answer.strip()

            form.answer = answer

        return form, branch if return_branch else form

    async def _extend(
        self,
        tools,
        reason,
        predict,
        score,
        select,
        plan,
        # image,
        allow_action,
        confidence,
        score_num_digits,
        score_range,
        select_choices,
        predict_num_sentences,
        **kwargs,
    ):
        """
        Handles the extension of the form based on the provided parameters.

        Args:
            form: Form data.
            tools: Tools data.
            reason: Flag indicating if reason should be included.
            predict: Flag indicating if prediction should be included.
            score: Flag indicating if score should be included.
            select: Flag indicating if selection should be included.
            plan: Flag indicating if plan should be included.
            allow_action: Flag indicating if action should be allowed.
            confidence: Flag indicating if confidence should be included.
            score_num_digits: Number of digits for score.
            score_range: Range for score.
            select_choices: Choices for selection.
            predict_num_sentences: Number of sentences for prediction.
            allow_extension: Flag indicating if extension should be allowed.
            max_extension: Maximum extension value.
            kwargs: Additional keyword arguments.

        Returns:
            list: The extended forms.
        """
        extension_forms = []

        # Ensure the next step in the plan is handled
        directive_kwargs = {
            "tools": tools,
            "reason": reason,
            "predict": predict,
            "score": score,
            "select": select,
            "allow_action": allow_action,
            "confidence": confidence,
            "score_num_digits": score_num_digits,
            "score_range": score_range,
            "select_choices": select_choices,
            "predict_num_sentences": predict_num_sentences,
            **kwargs,
        }

        if plan:
            keys = [f"step_{i+1}" for i in range(len(plan))]
            plan = validate_mapping(plan, keys, handle_unmatched="force")

            # If plan is provided, process each step
            for i in keys:
                directive_kwargs["instruction"] = plan[i]
                last_form = await self._direct(**directive_kwargs)
                last_form.is_extension = True
                extension_forms.append(last_form)
                directive_kwargs["max_extension"] -= 1
                if not getattr(last_form, "extension_required", None):
                    break

        else:
            # Handle single step extension
            last_form = await self._direct(**directive_kwargs)
            last_form.is_extension = True
            extension_forms.append(last_form)

        return extension_forms

    async def _act(self, form, branch, actions=None):
        """
        Processes actions based on the provided form and actions.

        Args:
            form: Form data.
            branch: Branch instance.
            actions: Actions data.

        Returns:
            dict: The updated form.
        """
        if getattr(form, "action_performed", None) is True:
            return form

        keys = [f"action_{i+1}" for i in range(len(actions))]
        actions = validate_mapping(actions, keys, handle_unmatched="force")

        try:
            requests = []
            for k in keys:
                _func = actions[k]["function"]
                _func = _func.replace("functions.", "")
                msg = ActionRequest(
                    function=_func,
                    arguments=actions[k]["arguments"],
                    sender=branch.ln_id,
                    recipient=branch.tool_manager.registry[_func].ln_id,
                )
                requests.append(msg)
                branch.add_message(action_request=msg)

            if requests:
                out = await self._process_action_request(
                    branch=branch, invoke_tool=True, action_request=requests
                )

                if out is False:
                    raise ValueError("No requests found.")

                len_actions = len(actions)
                action_responses = [
                    i
                    for i in branch.messages[-len_actions:]
                    if isinstance(i, ActionResponse)
                ]

                _action_responses = {}
                for idx, item in enumerate(action_responses):
                    _action_responses[f"action_{idx+1}"] = item._to_dict()

                form.append_to_request("action_response")
                if (a := getattr(form, "action_response", None)) is None:
                    form.add_field("action_response", {})

                len1 = len(form.action_response)
                for k, v in _action_responses.items():
                    while k in form.action_response:
                        k = f"{k}_1"
                    form.action_response[k] = v

                if len(form.action_response) > len1:
                    form.append_to_request("action_performed")
                    form.action_performed = True
                return form

        except Exception as e:
            raise ValueError(f"Error processing action request: {e}")

    async def _select(
        self,
        form=None,
        choices=None,
        reason=False,
        confidence_score=None,
        instruction=None,
        template=None,
        context=None,
        branch=None,
        **kwargs,
    ):
        """
        Selects a response based on the provided parameters.

        Args:
            form (Any, optional): Form to create instruction from.
            choices (Any, optional): Choices for the selection.
            reason (bool, optional): Whether to include a reason for the selection.
            confidence_score (Any, optional): Confidence score for the selection.
            instruction (Any, optional): Instruction for the selection.
            template (Any, optional): Template for the selection.
            context (Any, optional): Context to perform the selection on.
            branch (Any, optional): Branch to use for the selection.
            **kwargs: Additional arguments for the selection.

        Returns:
            Any: The selection response.
        """
        branch = branch or self.branch

        if not form:
            form = template(
                choices=choices,
                reason=reason,
                confidence_score=confidence_score,
                instruction=instruction,
                context=context,
            )

        return await self._chat(
            form=form, return_form=True, branch=branch, **kwargs
        )

    async def _predict(
        self,
        form=None,
        num_sentences=None,
        reason=False,
        confidence_score=None,
        instruction=None,
        context=None,
        branch=None,
        template=None,
        **kwargs,
    ):
        """
        Predicts a response based on the provided parameters.

        Args:
            form: Form data.
            num_sentences: Number of sentences for the prediction.
            reason: Flag indicating if reason should be included.
            confidence_score: Confidence score for the prediction.
            instruction: Instruction for the prediction.
            context: Context to perform the prediction on.
            branch: Branch instance.
            template: Template for the prediction.
            kwargs: Additional keyword arguments.

        Returns:
            Any: The prediction response.
        """
        branch = branch or self.branch

        if not form:
            form = template(
                instruction=instruction,
                context=context,
                num_sentences=num_sentences,
                confidence_score=confidence_score,
                reason=reason,
            )

        return await self._chat(
            form=form, return_form=True, branch=branch, **kwargs
        )

    async def _score(
        self,
        form=None,
        score_range=None,
        include_endpoints=None,
        num_digit=None,
        reason=False,
        confidence_score=None,
        instruction=None,
        context=None,
        branch=None,
        template=None,
        **kwargs,
    ):
        """
        Scores a response based on the provided parameters.

        Args:
            form: Form data.
            score_range: Range for score.
            include_endpoints: Flag indicating if endpoints should be included.
            num_digit: Number of digits for score.
            reason: Flag indicating if reason should be included.
            confidence_score: Confidence score for the score.
            instruction: Instruction for the score.
            context: Context to perform the score on.
            branch: Branch instance.
            template: Template for the score.
            kwargs: Additional keyword arguments.

        Returns:
            Any: The score response.
        """
        branch = branch or self.branch
        if not form:
            form = template(
                score_range=score_range,
                include_endpoints=include_endpoints,
                num_digit=num_digit,
                reason=reason,
                confidence_score=confidence_score,
                instruction=instruction,
                context=context,
            )

        return await self._chat(
            form=form, return_form=True, branch=branch, **kwargs
        )

    async def _plan(
        self,
        form=None,
        num_step=None,
        reason=False,
        confidence_score=None,
        instruction=None,
        context=None,
        branch=None,
        template=None,
        **kwargs,
    ):
        """
        Plans a response based on the provided parameters.

        Args:
            form: Form data.
            num_step: Number of steps for the plan.
            reason: Flag indicating if reason should be included.
            confidence_score: Confidence score for the plan.
            instruction: Instruction for the plan.
            context: Context to perform the plan on.
            branch: Branch instance.
            template: Template for the plan.
            kwargs: Additional keyword arguments.

        Returns:
            Any: The plan response.
        """
        branch = branch or self.branch
        template = template or self.default_template

        if not form:
            form = template(
                instruction=instruction,
                context=context,
                num_step=num_step,
                reason=reason,
                confidence_score=confidence_score,
            )

        return await self._chat(form=form, **kwargs)

    @staticmethod
    def _process_model_response(content_, requested_fields):
        """
        Processes the model response content.

        Args:
            content_: The content data.
            requested_fields: Fields requested in the response.

        Returns:
            Any: The processed response.
        """
        out_ = content_.get("content", "")
        if out_ == "":
            out_ = content_

        if requested_fields:
            with contextlib.suppress(Exception):
                return validate_mapping(
                    out_, requested_fields, handle_unmatched="force"
                )

        if isinstance(out_, str):
            with contextlib.suppress(Exception):
                return to_dict(out_, fuzzy_parse=True)

            with contextlib.suppress(Exception):
                return extract_block(out_)

            with contextlib.suppress(Exception):
                match = re.search(r"```json\n({.*?})\n```", out_, re.DOTALL)
                if match:
                    return to_dict(match.group(1), fuzzy_parse=True)

        return out_
