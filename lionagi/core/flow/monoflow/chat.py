from typing import Any

from lionagi.core.flow.base.baseflow import BaseMonoFlow
from lionagi.core.flow.monoflow.chat_mixin import MonoChatMixin


class MonoChat(BaseMonoFlow, MonoChatMixin):

    def __init__(self, branch) -> None:
        super().__init__(branch)

    async def chat(
        self,
        instruction,
        context=None,
        sender=None,
        system=None,
        tools=False,
        out: bool = True,
        invoke: bool = True,
        output_fields=None,
        **kwargs,
    ) -> Any:
        """
        a chat conversation with LLM, processing instructions and system messages, optionally invoking tools.

        Args:
                branch: The Branch instance to perform chat operations.
                instruction (Union[Instruction, str]): The instruction for the chat.
                context (Optional[Any]): Additional context for the chat.
                sender (Optional[str]): The sender of the chat message.
                system (Optional[Union[System, str, Dict[str, Any]]]): System message to be processed.
                tools (Union[bool, Tool, List[Tool], str, List[str]]): Specifies tools to be invoked.
                out (bool): If True, outputs the chat response.
                invoke (bool): If True, invokes tools as part of the chat.
                **kwargs: Arbitrary keyword arguments for chat completion.

        Examples:
                >>> await ChatFlow.chat(branch, "Ask about user preferences")
        """

        config = self._create_chat_config(
            instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            output_fields=output_fields,
            **kwargs,
        )

        await self._call_chatcompletion(**config)

        return await self._output(invoke, out, output_fields)
