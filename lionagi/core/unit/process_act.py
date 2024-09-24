"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Literal, Callable
from lion_core.libs import validate_mapping

from lion_core.session.branch import Branch
from lion_core.generic.note import note
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse
from lionagi.core.unit.process_action_request import process_action_request
from lionagi.core.unit.process_action_response import process_action_response
from lionagi.core.unit.unit_form import UnitForm


async def process_action(
    branch: Branch,
    form: UnitForm,
    actions: dict,
    handle_unmatched: Literal["ignore", "raise", "remove", "force"] = "force",
    return_branch: bool = False,
    invoke_action: bool = True,
    action_response_parser: Callable = None,
    action_parser_kwargs: dict = None,
) -> UnitForm | tuple[Branch, UnitForm]:

    if form._action_performed:
        return (branch, form) if return_branch else form

    action_keys = [f"action_{i+1}" for i in range(len(actions))]
    validated_actions = note(
        **validate_mapping(
            actions,
            action_keys,
            handle_unmatched=handle_unmatched,
        )
    )
    requests = []
    for k in action_keys:
        _func = validated_actions.get([k, "function"], "").replace("functions.", "")
        msg = ActionRequest(
            func=_func,
            arguments=validated_actions[k, "arguments"],
            sender=branch.ln_id,
            recipient=branch.tool_manager.registry[_func].ln_id,
        )
        requests.append(msg)
        branch.add_message(action_request=msg)

    if requests:
        out = await process_action_request(
            branch=branch,
            action_request=requests,
            invoke_action=invoke_action,
        )

        await process_action_response(
            branch=branch,
            action_requests=requests,
            responses=out,
            response_parser=action_response_parser,
            parser_kwargs=action_parser_kwargs,
        )

        len_actions = len(validated_actions)
        action_responses = [
            i for i in branch.messages[-len_actions:] if isinstance(i, ActionResponse)
        ]

        _res = note()

        len1 = len(form.action_response)
        for idx, item in enumerate(action_responses):
            _res.insert(["action", idx], item.to_dict())

        acts_ = _res.get(["action"], [])
        action_responses.extend(acts_)
        form.action_response.extend(
            [i for i in action_responses if i not in form.action_response]
        )

        if len(form.action_response) > len1:
            form._action_performed = True

    return (branch, form) if return_branch else form
