from abc import ABC
from lion_core.libs import validate_mapping
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse


class UnitActMixin(ABC):

    async def _act(self, form, branch, actions):
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
