from abc import ABC
from typing import Optional
from lion_core.libs import nmerge, validate_mapping
from lion_core.record.form import Form

from .utils import process_tools


class UnitDirectMixin(ABC):

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
        images: Optional[str] = None,
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
        images: Optional[str] = None,
        verbose=None,
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
                print(f"------------------- Extension completed -------------------\n")

            extension_forms.extend(new_form)
            last_form = new_form[-1] if isinstance(new_form, list) else new_form
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
