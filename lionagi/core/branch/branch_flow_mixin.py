from abc import ABC
from typing import Any, TypeVar

from lionagi.core.schema.base_node import TOOL_TYPE, Tool
from lionagi.core.flow.mono_chat import MonoChat
from lionagi.core.flow.mono_followup import MonoFollowup
from lionagi.core.flow.mono_react import MonoReAct

from lionagi.core.messages.schema import Instruction, System

T = TypeVar("T", bound=Tool)


class BranchFlowMixin(ABC):

    async def chat(
        self,
        instruction: Instruction | str,
        context: Any = None,
        sender: str = None,
        system: System | str | dict[str, Any] = None,
        tools: TOOL_TYPE = False,
        out: bool = True,
        invoke: bool = True,
        output_fields: dict | None = None,
        **kwargs,
    ) -> Any:
        """
        Initiates a chat interaction, potentially triggering tool usage based on the instruction.

        This method represents a single round of interaction with the LLM, which can optionally
        trigger a tool call and specify output fields for structured response.

        Args:
            instruction (Instruction | str): The instruction or prompt for the LLM.
            context (Any, optional): Additional context for the LLM.
            sender (str, optional): Identifier for the sender of the message.
            system (System | str | dict[str, Any], optional): System message to include.
            tools (TOOL_TYPE, optional): Indicates if tools should be considered during the chat.
            out (bool, optional): If True, formats the output as specified by `output_fields`.
            invoke (bool, optional): If True, allows invoking tools based on the conversation.
            output_fields (Any, optional): Specifies the fields to be included in the output dictionary.
            **kwargs: Additional keyword arguments for customization.

        Returns:
            Any: The result of the chat interaction, potentially including tool outputs.

        """
        flow = MonoChat(self)
        return await flow.chat(
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            out=out,
            invoke=invoke,
            output_fields=output_fields,
            **kwargs,
        )

    async def ReAct(
        self,
        instruction: Instruction | str | dict[str, dict | str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        auto=False,
        num_rounds: int = 1,
        reason_prompt=None,
        action_prompt=None,
        output_prompt=None,
        **kwargs,
    ):
        """
        Initiates a ReAct flow, where the LLM first reasons about its action plan then performs actions.

        The ReAct is a two-step process involving reasoning and action, which can have multiple
        rounds and may include automatic stopping if the LLM deems the task successfully achieved.

        Args:
            instruction (Instruction | str | dict[str, dict | str]): The instruction for the LLM.
            context (Any, optional): Additional context for the LLM.
            sender (str, optional): Identifier for the sender of the message.
            system (Any, optional): System message to include.
            tools (Any, optional): Indicates if tools should be used in the ReAct flow.
            auto (bool, optional): If True, allows automatic stopping before max rounds if the task is achieved.
            num_rounds (int, optional): The maximum number of rounds for ReAct.
            reason_prompt (Any, optional): Prompt for reasoning about the action plan.
            action_prompt (Any, optional): Prompt for performing actions.
            output_prompt (Any, optional): Prompt for structuring the output.
            **kwargs: Additional keyword arguments for customization.

        Returns:
            Any: The result of the ReAct flow, potentially including multiple rounds of reasoning and actions.

        """
        flow = MonoReAct(self)
        return await flow.ReAct(
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            auto=auto,
            num_rounds=num_rounds,
            reason_prompt=reason_prompt,
            action_prompt=action_prompt,
            output_prompt=output_prompt,
            **kwargs,
        )

    async def followup(
        self,
        instruction: Instruction | str | dict[str, dict | str],
        context: Any = None,
        sender: str = None,
        system: Any = None,
        tools: Any = None,
        max_followup: int = 1,
        auto: bool = False,
        followup_prompt: Any = None,
        output_prompt: Any = None,
        out: bool = True,
        **kwargs,
    ):
        """
        Initiates a follow-up interaction after a ReAct process, without the initial reasoning step.

        This method represents the continuation of the conversation with additional actions or
        tool invocations based on new or evolving instructions. Follow-ups can occur in multiple
        rounds, with the possibility of automatic cessation if the LLM determines the task has
        been successfully completed.

        Args:
            instruction (Instruction | str | dict[str, dict | str]): The follow-up instruction for the LLM.
            context (Any, optional): Additional context for the LLM.
            sender (str, optional): Identifier for the sender of the message.
            system (Any, optional): System message to include.
            tools (Any, optional): Indicates if tools should be used in the follow-up flow.
            max_followup (int, optional): The maximum number of follow-up rounds. Defaults to 1.
            auto (bool, optional): If True, allows automatic stopping of the follow-up before reaching
                                   max_followup rounds if the LLM deems the task as successfully achieved.
            followup_prompt (Any, optional): The prompt used for follow-up interactions.
            output_prompt (Any, optional): The prompt for structuring the output.
            out (bool, optional): If True, outputs the response as specified by `output_fields`.
            **kwargs: Additional keyword arguments for customization.

        Returns:
            Any: The result of the follow-up interaction, potentially including outputs from tool usage.

        """
        flow = MonoFollowup(self)
        return await flow.followup(
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            max_followup=max_followup,
            auto=auto,
            followup_prompt=followup_prompt,
            output_prompt=output_prompt,
            out=out,
            **kwargs,
        )
