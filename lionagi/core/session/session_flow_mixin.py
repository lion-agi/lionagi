from abc import ABC

from lionagi.core.schema.base_node import TOOL_TYPE
from lionagi.core.messages.system import System
from lionagi.core.messages.instruction import Instruction
from lionagi.core.branch.branch import Branch
from lionagi.core.flow.poly_chat import PolyChat


class SessionFlowMIxin(ABC):

    async def call_chatcompletion(
        self,
        branch: Branch | str | None = None,
        sender: str | None = None,
        with_sender=False,
        **kwargs,
    ):
        """
        Asynchronously calls the chat completion service with the current message queue.

        This method prepares the messages for chat completion, sends the request to the configured service, and handles the response. The method supports additional keyword arguments that are passed directly to the service.

        Args:
            sender (str | None): The name of the sender to be included in the chat completion request. Defaults to None.
            with_sender (bool): If True, includes the sender's name in the messages. Defaults to False.
            **kwargs: Arbitrary keyword arguments passed directly to the chat completion service.

        Examples:
            >>> await branch.call_chatcompletion()
        """
        branch = self.get_branch(branch)
        await branch.call_chatcompletion(
            sender=sender,
            with_sender=with_sender,
            **kwargs,
        )

    async def chat(
        self,
        instruction: dict | list | Instruction | str,
        branch: Branch | str | None = None,
        context: dict | list | str = None,
        sender: str | None = None,
        system: dict | list | System | None = None,
        tools: TOOL_TYPE = False,
        out: bool = True,
        invoke: bool = True,
        output_fields=None,
        **kwargs,
    ) -> str | None:
        """
        a chat conversation with LLM, processing instructions and system messages, optionally invoking tools.

        Args:
            branch: The Branch instance to perform chat operations.
            instruction (dict | list | Instruction | str): The instruction for the chat.
            context (Optional[Any]): Additional context for the chat.
            sender (str | None): The sender of the chat message.
            system (Optional[Union[System, str, dict[str, Any]]]): System message to be processed.
            tools (Union[bool, Tool, List[Tool], str, List[str]]): Specifies tools to be invoked.
            out (bool): If True, outputs the chat response.
            invoke (bool): If True, invokes tools as part of the chat.
            **kwargs: Arbitrary keyword arguments for chat completion.

        Examples:
            >>> await ChatFlow.chat(branch, "Ask about user preferences")
        """

        branch = self.get_branch(branch)
        return await branch.chat(
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
        instruction: dict | list | Instruction | str,
        branch: Branch | str | None = None,
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
        Performs a reason-tool cycle with optional tool invocation over multiple rounds.

        Args:
            branch: The Branch instance to perform ReAct operations.
            instruction (dict | list | Instruction | str): Initial instruction for the cycle.
            context: Context relevant to the instruction.
            sender (str | None): Identifier for the message sender.
            system: Initial system message or configuration.
            tools: Tools to be registered or used during the cycle.
            num_rounds (int): Number of reason-tool cycles to perform.
            **kwargs: Additional keyword arguments for customization.

        Examples:
            >>> await ChatFlow.ReAct(branch, "Analyze user feedback", num_rounds=2)
        """
        branch = self.get_branch(branch)

        return await branch.ReAct(
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
        instruction: dict | list | Instruction | str,
        branch=None,
        context=None,
        sender=None,
        system=None,
        tools=None,
        max_followup: int = 1,
        auto=False,
        followup_prompt=None,
        output_prompt=None,
        out=True,
        **kwargs,
    ):
        """
        Automatically performs follow-up tools based on chat intertools and tool invocations.

        Args:
            branch: The Branch instance to perform follow-up operations.
            instruction (dict | list | Instruction | str): The initial instruction for follow-up.
            context: Context relevant to the instruction.
            sender (str | None): Identifier for the message sender.
            system: Initial system message or configuration.
            tools: Specifies tools to be considered for follow-up tools.
            max_followup (int): Maximum number of follow-up chats allowed.
            out (bool): If True, outputs the result of the follow-up tool.
            **kwargs: Additional keyword arguments for follow-up customization.

        Examples:
            >>> await ChatFlow.auto_followup(branch, "Finalize report", max_followup=2)
        """
        branch = self.get_branch(branch)
        return await branch.followup(
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

    async def parallel_chat(
        self,
        instruction: Instruction | str,
        num_instances=1,
        context=None,
        sender=None,
        branch_system=None,
        messages=None,
        tools=False,
        out=True,
        invoke: bool = True,
        output_fields=None,
        persist_path=None,
        branch_config={},
        explode=False,
        **kwargs,
    ):
        """
        parallel chat
        """

        flow = PolyChat(self)

        return await flow.parallel_chat(
            instruction,
            num_instances=num_instances,
            context=context,
            sender=sender,
            branch_system=branch_system,
            messages=messages,
            tools=tools,
            out=out,
            invoke=invoke,
            output_fields=output_fields,
            persist_path=persist_path,
            branch_config=branch_config,
            explode=explode,
            **kwargs,
        )
