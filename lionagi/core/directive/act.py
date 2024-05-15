from lionagi.libs.ln_convert import to_list
from ..message.action_request import ActionRequest
from ..message.action_response import ActionResponse

from .chat import Chat
from .util import process_tools

from lionagi.core.generic.abc import Field
from .base import DirectiveTemplate
from .chain import Chain


class ActionTemplate(DirectiveTemplate):
    template_name: str = "Action"

    action_required: bool = Field(
        False, description="true if actions are needed else false"
    )

    actions: list[dict] = Field(
        None,
        description="""
provide The list of action(s) to take, each action in format of 
{"function": function_name, "arguments": {param1:..., param2:..., ...}}. 
Leave blank if no further actions are needed, 
you must use provided parameters for each action, DO NOT MAKE UP NAME!!!
""",
    )

    answer: str | dict | None = Field(
        default_factory=str,
        description="output answer to the questions asked if further actions are not needed, leave blank if an accurate answer cannot be provided from context during this step",
    )

    signature: str = "task -> reason, action_needed, actions, answer"

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        confidence_score=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = f"""
Perform reasoning and prepare actions with GIVEN TOOLS ONLY.
1. additional objective: {instruction or "N/A"}. 
2. additional information: {context or "N/A"}.
3. Absolutely DO NOT MAKE UP FUNCTIONS !!!
"""
        if confidence_score:
            self.append_to_request("confidence_score")


class Act(Chat):

    defalut_template = ActionTemplate

    async def act(
        self,
        context=None,
        instruction=None,
        *,
        system=None,
        sender=None,
        recipient=None,
        confidence_score=None,
        requested_fields=None,
        form=None,
        tools=False,
        invoke_tool=True,
        return_form=True,
        strict=False,
        rulebook=None,
        imodel=None,
        template_name=None,
        use_annotation=True,
        retries: int = 3,
        delay: float = 0,
        backoff_factor: float = 1,
        default=None,
        timeout: float | None = None,
        timing: bool = False,
        max_concurrency: int = 10_000,
        throttle_period: int = None,
        **kwargs,
    ):

        return await self._act(
            context=context,
            instruction=instruction,
            system=system,
            sender=sender,
            recipient=recipient,
            confidence_score=confidence_score,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            invoke_tool=invoke_tool,
            return_form=return_form,
            strict=strict,
            rulebook=rulebook,
            imodel=imodel,
            template_name=template_name,
            use_annotation=use_annotation,
            retries=retries,
            delay=delay,
            backoff_factor=backoff_factor,
            default=default,
            timeout=timeout,
            timing=timing,
            max_concurrency=max_concurrency,
            throttle_period=throttle_period,
            **kwargs,
        )

    async def _act(
        self,
        form=None,
        branch=None,
        tools=None,
        confidence_score=None,
        instruction=None,
        context=None,
        return_branch=False,
        **kwargs,
    ):
        branch = branch or self.branch
        if not form:
            form = self.default_template(
                confidence_score=confidence_score,
                instruction=instruction,
                context=context,
            )

        if tools:
            process_tools(tools, branch)

        form, branch = await self.chat(
            form=form,
            return_form=True,
            return_branch=True,
            branch=branch or self.branch,
            tools=tools,
            **kwargs,
        )

        if getattr(form, "action_needed", False):
            actions = getattr(form, "actions", None)
            if actions:
                actions = [actions] if not isinstance(actions, list) else actions

                try:
                    requests = []
                    for action in actions:
                        msg = ActionRequest(
                            function=action["function"],
                            arguments=action["arguments"],
                            sender=branch.ln_id,
                            recipient=branch.tool_manager.registry[
                                action["function"]
                            ].ln_id,
                        )
                        requests.append(msg)

                    if requests:
                        out = self._process_action_request(
                            branch=branch, invoke_tool=True, action_request=requests
                        )

                        if out == False:
                            raise ValueError(
                                "Error processing action request: No requests found."
                            )

                        len_actions = len(actions)
                        action_responses = branch.messages[-len_actions:]

                        if not all(
                            isinstance(i, ActionResponse) for i in action_responses
                        ):
                            raise ValueError(
                                "Error processing action request: Invalid action response."
                            )

                        action_responses = [i._to_dict() for i in action_responses]
                        form._add_field(
                            "action_response", list[dict], None, action_responses
                        )
                except Exception as e:
                    raise ValueError(f"Error processing action request: {e}")
            raise ValueError("Error processing action request: No requests found.")

        return form, branch if return_branch else form

    async def direct(self, *args, **kwargs):
        return await self.act(*args, **kwargs)

    async def chain_of_act(
        self,
        context=None,
        instruction=None,
        confidence_score=None,
        return_branch=False,
        rulebook=None,
        branch=None,
        imodel=None,
        num_step=None,
        plan_params={},
        plan_kwargs={},
    ):

        branch = branch or self.branch
        cot = Chain(branch=branch)

        cot_form, branch = await cot.chain(
            context=context,
            instruction=instruction,
            confidence_score=confidence_score,
            rulebook=rulebook,
            imodel=imodel,
            num_step=num_step,
            plan_params=plan_params,
            plan_kwargs=plan_kwargs,
            return_branch=True,
            reason=True,
            directive_obj=self,
        )

        act_forms = cot_form.chain_forms
        fields = ["answer", "reason", "actions", "action_response"]
        for i in fields:
            _v = [getattr(j, i, None) for j in act_forms]
            _v = to_list(_v, flatten=True, dropna=True)
            cot_form._add_field(
                field=f"chain_{i}", annotation=list, default=None, value=_v
            )

        if return_branch:
            return cot_form, branch

        return cot_form
