from __future__ import annotations

from lionagi.core.action.tool import Tool
from lionagi.core.message import Instruction, System
from lionagi.core.session.branch import Branch


def _create_chat_config(
    system: dict | str | System | None = None,
    instruction: dict | str | Instruction | None = None,
    context: str | dict | None = None,
    requested_fields: dict | None = None,
    tools: list[Tool | str] | bool = False,
    branch: Branch | None = None,
    sender: str | None = None,
    system_sender: str | None = None,
    **kwargs,  # model_kwargs
):
    if system:
        branch.add_message(system=system)

    def _create_chat_config(
        self,
        system: str | None = None,
        instruction: str | None = None,
        images: str | None = None,
        sender: str | None = None,
        recipient: str | None = None,
        requested_fields: list | None = None,
        form: Form = None,
        tools: bool = False,
        branch: Any | None = None,
        **kwargs,
    ) -> Any:

        branch = branch or self.branch

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
