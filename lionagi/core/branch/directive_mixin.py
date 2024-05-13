from abc import ABC
from typing import Any, Optional, Union, TypeVar


class DirectiveMixin(ABC):

    async def chat(
        self,
        instruction=None,  # Instruction node - JSON serializable
        *,
        system=None,  # system node - JSON serializable
        context=None,  # JSON serializable
        sender=None,  # str
        recipient=None,  # str
        requested_fields=None,  # dict[str, str]
        form=None,
        tools=False,
        invoke_tool=True,
        return_form=True,
        strict=False,
        validator=None,
        imodel=None,
        **kwargs,
    ) -> Any:
        from lionagi.core.directive.chat import Chat

        directive = Chat(self)
        return await directive.chat(
            instruction=instruction,
            system=system,
            context=context,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            invoke_tool=invoke_tool,
            return_form=return_form,
            strict=strict,
            validator=validator,
            imodel=imodel,
            **kwargs,
        )

    # async def ReAct(
    #     self,
    #     instruction: Instruction | str | dict[str, dict | str],
    #     context=None,
    #     sender=None,
    #     system=None,
    #     tools=None,
    #     auto=False,
    #     num_rounds: int = 1,
    #     reason_prompt=None,
    #     action_prompt=None,
    #     output_prompt=None,
    #     **kwargs,
    # ):
    #     flow = MonoReAct(self)
    #     return await flow.ReAct(
    #         instruction=instruction,
    #         context=context,
    #         sender=sender,
    #         system=system,
    #         tools=tools,
    #         auto=auto,
    #         num_rounds=num_rounds,
    #         reason_prompt=reason_prompt,
    #         action_prompt=action_prompt,
    #         output_prompt=output_prompt,
    #         **kwargs,
    #     )

    # async def followup(
    #     self,
    #     instruction: Instruction | str | dict[str, dict | str],
    #     context=None,
    #     sender=None,
    #     system=None,
    #     tools=None,
    #     max_followup: int = 1,
    #     auto=False,
    #     followup_prompt=None,
    #     output_prompt=None,
    #     out=True,
    #     **kwargs,
    # ):
    #     flow = MonoFollowup(self)
    #     return await flow.followup(
    #         instruction=instruction,
    #         context=context,
    #         sender=sender,
    #         system=system,
    #         tools=tools,
    #         max_followup=max_followup,
    #         auto=auto,
    #         followup_prompt=followup_prompt,
    #         output_prompt=output_prompt,
    #         out=out,
    #         **kwargs,
    #     )
