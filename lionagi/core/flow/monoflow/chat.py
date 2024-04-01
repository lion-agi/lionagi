"""
This module contains the MonoChat class for performing chat conversations with an LLM.

The MonoChat class allows for processing instructions and system messages, and optionally invoking tools during the chat conversation.
It extends the BaseMonoFlow and MonoChatMixin classes.
"""

from typing import Any

from lionagi.core.flow.baseflow import BaseMonoFlow
from lionagi.core.flow.monoflow.chat_mixin import MonoChatMixin


class MonoChat(BaseMonoFlow, MonoChatMixin):
    """
    A class for performing a chat conversation with an LLM, processing instructions and system messages, and optionally invoking tools.

    Attributes:
        branch (Branch): The Branch instance to perform chat operations.

    Methods:
        __init__(self, branch: Branch) -> None:
            Initializes the MonoChat instance with the specified Branch.

        async chat(self, instruction: Union[Instruction, str] = None, context: Any = None, sender: str = None,
                   system: Union[System, str, Dict[str, Any]] = None, tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
                   out: bool = True, invoke: bool = True, output_fields: Any = None, prompt_template: Any = None, **kwargs) -> Any:
            Performs a chat conversation with an LLM, processing instructions and system messages, and optionally invoking tools.

            Args:
                instruction (Union[Instruction, str], optional): The instruction for the chat. Defaults to None.
                context (Any, optional): Additional context for the chat. Defaults to None.
                sender (str, optional): The sender of the chat message. Defaults to None.
                system (Union[System, str, Dict[str, Any]], optional): System message to be processed. Defaults to None.
                tools (Union[bool, Tool, List[Tool], str, List[str]], optional): Specifies tools to be invoked. Defaults to False.
                out (bool, optional): If True, outputs the chat response. Defaults to True.
                invoke (bool, optional): If True, invokes tools as part of the chat. Defaults to True.
                output_fields (Any, optional): The output fields for the chat. Defaults to None.
                prompt_template (Any, optional): The prompt template for the chat. Defaults to None.
                **kwargs: Arbitrary keyword arguments for chat completion.

            Returns:
                Any: The result of the chat conversation.

            Examples:
                >>> await MonoChat.chat(branch, "Ask about user preferences")
    """

    def __init__(self, branch) -> None:
        """
        Initializes the MonoChat instance.

        Args:
            branch (Branch): The Branch instance to perform chat operations.
        """
        super().__init__(branch)

    async def chat(
        self,
        instruction=None,
        context=None,
        sender=None,
        system=None,
        tools=False,
        out: bool = True,
        invoke: bool = True,
        output_fields=None,
        prompt_template=None,
        **kwargs,
    ) -> Any:
        """
        Performs a chat conversation with an LLM, processing instructions and system messages, and optionally invoking tools.

        Args:
            instruction (Union[Instruction, str], optional): The instruction for the chat. Defaults to None.
            context (Any, optional): Additional context for the chat. Defaults to None.
            sender (str, optional): The sender of the chat message. Defaults to None.
            system (Union[System, str, Dict[str, Any]], optional): System message to be processed. Defaults to None.
            tools (Union[bool, Tool, List[Tool], str, List[str]], optional): Specifies tools to be invoked. Defaults to False.
            out (bool, optional): If True, outputs the chat response. Defaults to True.
            invoke (bool, optional): If True, invokes tools as part of the chat. Defaults to True.
            output_fields (Any, optional): The output fields for the chat. Defaults to None.
            prompt_template (Any, optional): The prompt template for the chat. Defaults to None.
            **kwargs: Arbitrary keyword arguments for chat completion.

        Returns:
            Any: The result of the chat conversation.

        Examples:
            >>> await MonoChat.chat(branch, "Ask about user preferences")
        """

        config = self._create_chat_config(
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            prompt_template=prompt_template,
            tools=tools,
            output_fields=output_fields,
            **kwargs,
        )

        await self._call_chatcompletion(**config)

        return await self._output(
            invoke=invoke,
            out=out,
            output_fields=output_fields,
            prompt_template=prompt_template,
        )
