from lionagi.core.message.action_request import ActionRequest
from lionagi.core.message.action_response import ActionResponse
from lionagi.core.generic.abc import Field, Component
from lionagi.core.report.form import Form
from lionagi.libs.ln_func_call import rcall
from .base import Chat
from .util import process_tools


class ActionTemplate(Form):
    confidence_score: float | None = Field(
        None,
        description="a numeric score between 0 to 1 formatted in num:0.2f, 1 being very confident and 0 being not confident at all, just guessing",
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        },
    )

    reason: str | None = Field(
        "",
        description="brief reason for the given output, format: This is my best response because ...",
    )

    template_name: str = "Action"

    action_required: bool | None = Field(
        None, description="True if actions are needed else False"
    )

    actions: list[dict] | None = Field(
        None,
        description="""
provide The list of action(s) to take, [{"function": func, "arguments": {"param1":..., "param2":..., ...}}, ...] Leave blank if no further actions are needed, you must use provided parameters for each action, DO NOT MAKE UP NAME!!!
""",
    )

    answer: str | None = Field(
        None,
        description="output answer to the questions asked if further actions are not needed, leave blank if an accurate answer cannot be provided from context during this step",
    )

    assignment: str = "task -> reason, action_required, actions, answer"

    def __init__(
        self,
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
            form = ActionTemplate(
                confidence_score=confidence_score,
                instruction=instruction,
                context=context,
            )

        if tools:
            process_tools(tools, branch)

        form, branch = await self.chat(
            form=form,
            return_branch=True,
            branch=branch,
            tools=tools,
            **kwargs,
        )

        if getattr(form, "action_required", False):
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
                        self.branch.add_message(msg)

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

    async def act(self, *args, **kwargs):
        return await rcall(self._act, *args, **kwargs)

    async def direct(self, *args, **kwargs):
        return await self.act(*args, **kwargs)
