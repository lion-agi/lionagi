from typing import Callable
from .chat import Chat
from ..message import Instruction
from ..action import Tool


class Followup(Chat):

    FOLLOWUP_PROMPT = """
    In the current task, you are allowed a maximum of another {num_followup} followup chats. 
    If further actions are needed, invoke tool usage. 
    If you are done, present the final result to the user without further tool usage.
    """

    OUTPUT_PROMPT = "Notice: Present the final output to the user. Original user instruction: {instruction}"

    async def followup(
        self,
        system=None,  # system node - JSON serializable
        instruction=None,  # Instruction node - JSON serializable
        context=None,  # JSON serializable
        sender=None,  # str
        recipient=None,  # str
        requested_fields=None,  # dict[str, str]
        form=None,
        tools=False,
        max_followup: int = 1,
        followup_prompt=None,
        output_prompt=None,
        **kwargs,
    ):
        return await self._followup(
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            max_followup=max_followup,
            followup_prompt=followup_prompt,
            output_prompt=output_prompt,
            **kwargs,
        )

    @staticmethod
    def _get_prompt(prompt=None, default=None, num_followup=None, instruction=None):
        if prompt is not None:
            return prompt

        try:
            if num_followup is not None:
                return default.format(num_followup=num_followup)
            elif instruction is not None:
                return default.format(instruction=instruction)
        except (KeyError, ValueError):
            pass

        return default

    def _create_followup_config(self, tools, tool_choice="auto", **kwargs):
        if tools and isinstance(tools, list) and isinstance(tools[0], (Callable, Tool)):
            self.branch.tool_manager.register_tools(tools)

        if not self.branch.tool_manager.registry:
            raise ValueError("No tools found. You need to register tools.")

        if tools is None:
            tools = True
        config = self.branch.tool_manager.parse_tool(tools=tools, **kwargs)
        config["tool_parsed"] = True
        config["tool_choice"] = tool_choice
        return config

    async def followup(
        self,
        system=None,
        instruction=None,
        context=None,
        sender=None,
        recipient=None,
        requested_fields=None,
        form=None,
        tools=False,
        max_followup: int = 2,
        auto=True,
        followup_prompt=None,
        output_prompt=None,
        out=True,
        **kwargs,
    ) -> None:
        config = self._create_followup_config(tools, **kwargs)

        i = 0
        _out = ""

        while i < max_followup:
            _prompt = self._get_prompt(
                prompt=followup_prompt,
                default=self.FOLLOWUP_PROMPT,
                num_followup=max_followup - i,
            )

            if i == 0:
                _prompt = {"NOTICE": _prompt, "TASK": instruction}
                _out = await self.chat(
                    system=system,
                    instruction=_prompt,
                    context=context,
                    sender=sender,
                    recipient=recipient,
                    requested_fields=requested_fields,
                    **config,
                )

            else:
                _out = await self.chat(_prompt, sender=sender, **config)

            if not self.branch._is_invoked():
                return _out if out else None

            i += 1

        if not self.branch._is_invoked():
            return _out if out else None

        _prompt = self._get_prompt(
            prompt=output_prompt,
            default=self.OUTPUT_PROMPT,
            instruction=instruction,
        )
        _out = await self.chat(
            _prompt, sender=sender, requested_fields=requested_fields, **kwargs
        )
        return _out if out else None
