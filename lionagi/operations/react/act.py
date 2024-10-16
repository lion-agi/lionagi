import asyncio
from collections.abc import Callable
from typing import Literal

from lion_core.action.function_calling import FunctionCalling

from lionagi.core.action.tool import Tool
from lionagi.core.message.action_request import ActionRequest
from lionagi.core.message.action_response import ActionResponse
from lionagi.core.session.branch import Branch

from ..step_model import ReasonStepModel, StepModel
from .action_model import ActionResponseModel, ReasonActionResponseModel

PROMPT = """
Please {max_num_actions} number of actions to be performed only using the following tool_schema(s):\n {tool_schemas}. \n\n --- \n
"""


async def act(
    tools: list[Tool | Callable] | bool = True,
    min_num_actions: int = 1,
    max_num_actions: int | Literal["auto"] = "auto",
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    reason: bool = False,
    branch: Branch = None,
    return_branch=False,
    invoke_tool: bool = True,
    verbose_action: bool = False,
    **kwargs,  # additional chat arguments
) -> StepModel | ReasonStepModel:

    if min_num_actions < 1:
        raise ValueError("min_num_actions must be greater than 0")
    if max_num_actions != "auto" and max_num_actions < min_num_actions:
        raise ValueError(
            "max_num_actions must be 'auto' or an integer greater than or equal to min_num_actions"
        )

    branch = branch or Branch()
    if tools is True and not branch.tool_manager.registry:
        raise ValueError("No tools registered in the branch")

    if not isinstance(tools, bool):
        branch.register_tools(tools)

    tool_schemas = branch.tool_manager.get_tool_schema(tools)
    msg = f"Provide at least {min_num_actions}"

    if max_num_actions == "auto":
        msg += " and sufficient"
    elif max_num_actions == min_num_actions:
        msg = f"Provide exactly {max_num_actions}"
    else:
        msg += f" and up to {max_num_actions}"

    prompt = PROMPT.format(max_num_actions=msg, tool_schemas=tool_schemas)
    if instruction:
        prompt = f"{instruction}\n\n{prompt} \n\n "

    response: StepModel | ReasonStepModel = await branch.chat(
        instruction=prompt,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        pydantic_model=StepModel if not reason else ReasonStepModel,
        return_pydantic_model=True,
        **kwargs,
    )
    action_response_models = []
    action_response_model = (
        ActionResponseModel if not reason else ReasonActionResponseModel
    )

    results = None
    if response.actions:
        if verbose_action:
            print("Find action requests in model response.")

        action_requests: list[ActionRequest] = []
        func_calls = []
        for i in response.actions:
            if i.function in branch.tool_manager.registry:
                tool = branch.tool_manager.registry[i.function]
                action_requests.append(
                    ActionRequest(
                        function=i.function,
                        arguments=i.arguments,
                    )
                )
                _func_call = FunctionCalling(
                    func_tool=tool,
                    arguments=i.arguments,
                )
                func_calls.append(asyncio.create_task(_func_call.invoke()))

        if invoke_tool:
            results = await asyncio.gather(*func_calls)

            for idx, i in enumerate(results):
                action_response = ActionResponse(
                    action_request=action_requests[idx], func_outputs=i
                )
                action_requests[idx].action_response = action_response.ln_id
                branch.add_message(action_request=action_requests[idx])
                branch.add_message(action_response=action_response)

                data = response.actions[idx].model_dump()
                data["response"] = results
                out = action_response_model.model_validate(data)
                action_response_models.append(out)

            response.actions = action_response_models
            if verbose_action:
                print(
                    "Actions performed. Action requests and responses added to the branch."
                )

        else:
            for i in action_requests:
                branch.add_message(action_request=i)
            if verbose_action:
                print(
                    "Actions are now allowed for execution. Action requests added to the branch."
                )
    else:
        if verbose_action:
            print("No actions provided.")

    if return_branch:
        return response, branch
    return response
