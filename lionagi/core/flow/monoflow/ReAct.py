from typing import Callable
from .chat import MonoChat
from lionagi.core.schema import Tool
from lionagi.core.messages import Instruction


class MonoReAct(MonoChat):

    REASON_PROMPT = """
You have {num_steps} steps left in the current task. If available, integrate previous tool responses. Perform reasoning and prepare an action plan according to available tools only. Apply divide and conquer technique.
    """

    ACTION_PROMPT = """
You have {num_steps} steps left in the current task. If further actions are needed, invoke tool usage. If you are done, present the final result to the user without further tool usage.
    """

    OUTPUT_PROMPT = "Notice: Present the final output to the user. Original user instruction: {instruction}"

    async def ReAct(
        self,
        instruction: Instruction | str | dict[str, dict | str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        num_rounds: int = 1,
        reason_prompt=None,
        action_prompt=None,
        output_prompt=None,
        **kwargs,
    ):
        return await self._ReAct(
            instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            num_rounds=num_rounds,
            reason_prompt=reason_prompt,
            action_prompt=action_prompt,
            output_prompt=output_prompt,
            **kwargs,
        )

    @staticmethod
    def _get_prompt(prompt=None, default=None, num_steps=None, instruction=None):
        if prompt is not None:
            return prompt

        try:
            if num_steps is not None:
                return default.format(num_steps=num_steps)
            elif instruction is not None:
                return default.format(instruction=instruction)
        except (KeyError, ValueError):
            pass

        return default

    def _create_followup_config(self, tools, tool_choice="auto", **kwargs):
        if tools and isinstance(tools, list) and isinstance(tools[0], (Callable, Tool)):
            self.branch.tool_manager.register_tools(tools)

        if not self.branch.tool_manager.has_tools:
            raise ValueError("No tools found. You need to register tools.")

        config = self.branch.tool_manager.parse_tool(tools=True, **kwargs)
        config["tool_parsed"] = True
        config["tool_choice"] = tool_choice
        return config

    async def _ReAct(
        self,
        instruction: Instruction | str | dict[str, dict | str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        num_rounds: int = 1,
        auto=False,
        reason_prompt=None,
        action_prompt=None,
        output_prompt=None,
        out=True,
        **kwargs,
    ):

        config = self._create_followup_config(tools, **kwargs)

        i = 0
        _out = ""

        while i < num_rounds:
            _prompt = self._get_prompt(
                prompt=reason_prompt,
                default=self.REASON_PROMPT,
                num_steps=(num_rounds - i) * 2,
            )
            _instruct = {"NOTICE": _prompt}

            # reason
            if i == 0:
                _instruct["TASK"] = instruction

                await self.chat(
                    _instruct, context=context, sender=sender, system=system, **kwargs
                )

            elif i > 0:
                await self.chat(_instruct, sender=sender, **kwargs)

            # action
            _prompt = self._get_prompt(
                prompt=action_prompt,
                default=self.ACTION_PROMPT,
                num_steps=(num_rounds - i) * 2 - 1,
            )

            _out = await self.chat(_prompt, sender=sender, **config)

            if auto and not self.branch._is_invoked():
                return _out if out else None

            i += 1

        if auto:
            if not self.branch._is_invoked():
                return _out if out else None

            _prompt = self._get_prompt(
                prompt=output_prompt,
                default=self.OUTPUT_PROMPT,
                instruction=instruction,
            )
            _out = await self.chat(_prompt, sender=sender, **kwargs)
            return _out if out else None
